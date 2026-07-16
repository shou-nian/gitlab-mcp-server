"""只读 GitLab REST API 异步客户端。"""

from collections.abc import Mapping
from typing import Any
from urllib.parse import quote

import httpx

from gitlab_mcp.config import Settings
from gitlab_mcp.utils.logger import get_logger

logger = get_logger(__name__)


class GitLabClientError(RuntimeError):
    """GitLab 请求失败。"""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """返回可被 MCP 序列化的错误信息。"""

        result: dict[str, Any] = {"message": self.message}
        if self.status_code is not None:
            result["status_code"] = self.status_code
        if self.details is not None:
            result["details"] = self.details
        return result


class GitLabClient:
    """封装认证、超时、错误处理和只读 GitLab API。"""

    def __init__(
        self,
        settings: Settings,
        *,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.AsyncClient(
            base_url=settings.gitlab_api_url,
            headers={"PRIVATE-TOKEN": settings.gitlab_token.get_secret_value()},
            timeout=settings.gitlab_timeout,
        )

    async def __aenter__(self) -> "GitLabClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        """关闭客户端拥有的连接池。"""

        if self._owns_http_client:
            await self._http_client.aclose()

    async def get_project(self, project_id: int | str) -> dict[str, Any]:
        return await self._get(f"/projects/{_encode_path_value(project_id)}")

    async def get_file(
        self,
        project_id: int | str,
        file_path: str,
        ref: str,
    ) -> dict[str, Any]:
        project = _encode_path_value(project_id)
        file = _encode_path_value(file_path)
        return await self._get(
            f"/projects/{project}/repository/files/{file}",
            params={"ref": ref},
        )

    async def list_files(
        self,
        project_id: int | str,
        *,
        path: str = "",
        ref: str | None = None,
        recursive: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, str | int] = {
            "path": path,
            "recursive": str(recursive).lower(),
            "per_page": 100,
        }
        if ref is not None:
            params["ref"] = ref

        project = _encode_path_value(project_id)
        return await self._get_all_pages(
            f"/projects/{project}/repository/tree",
            params=params,
        )

    async def get_merge_request(
        self,
        project_id: int | str,
        merge_request_iid: int,
    ) -> dict[str, Any]:
        project = _encode_path_value(project_id)
        return await self._get(f"/projects/{project}/merge_requests/{merge_request_iid}")

    async def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
    ) -> dict[str, Any]:
        response = await self._request(path, params=params)
        payload = _parse_json(response)
        if not isinstance(payload, dict):
            raise GitLabClientError("GitLab 返回了非对象 JSON 响应")
        return payload

    async def _get_all_pages(
        self,
        path: str,
        *,
        params: Mapping[str, str | int],
    ) -> list[dict[str, Any]]:
        page = 1
        items: list[dict[str, Any]] = []
        while True:
            page_params = {**params, "page": page}
            response = await self._request(path, params=page_params)
            payload = _parse_json(response)
            if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
                raise GitLabClientError("GitLab 返回了非数组 JSON 响应")
            items.extend(payload)

            next_page = response.headers.get("x-next-page", "")
            if not next_page:
                return items
            try:
                page = int(next_page)
            except ValueError as exc:
                raise GitLabClientError("GitLab 返回了无效的分页信息") from exc

    async def _request(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
    ) -> httpx.Response:
        logger.info("GitLab request method=GET path=%s", path)
        try:
            response = await self._http_client.get(path, params=params)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.warning("GitLab request timeout path=%s", path)
            raise GitLabClientError("GitLab 请求超时") from exc
        except httpx.HTTPStatusError as exc:
            details = _safe_error_details(exc.response)
            logger.warning(
                "GitLab request failed path=%s status=%s",
                path,
                exc.response.status_code,
            )
            raise GitLabClientError(
                "GitLab API 请求失败",
                status_code=exc.response.status_code,
                details=details,
            ) from exc
        except httpx.RequestError as exc:
            logger.warning("GitLab connection failed path=%s error=%s", path, type(exc).__name__)
            raise GitLabClientError("无法连接 GitLab") from exc

        logger.info("GitLab response path=%s status=%s", path, response.status_code)
        return response


def _encode_path_value(value: int | str) -> str:
    """编码 GitLab URL 路径参数，支持 namespace/project 形式的项目标识。"""

    return quote(str(value), safe="")


def _parse_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError as exc:
        raise GitLabClientError("GitLab 返回了无效的 JSON 响应") from exc


def _safe_error_details(response: httpx.Response) -> Any:
    try:
        payload = response.json()
    except ValueError:
        return None
    return payload
