"""仓库文件查询 Tool。"""

from pydantic import ValidationError

from gitlab_mcp.gitlab.client import GitLabClient, GitLabClientError
from gitlab_mcp.gitlab.models import RepositoryFile, RepositoryTreeItem
from gitlab_mcp.tools import (
    ToolResponse,
    client_error_response,
    parameter_error,
    response_validation_error,
    success_response,
    validate_non_empty,
    validate_project_id,
)
from gitlab_mcp.utils.logger import get_logger

logger = get_logger(__name__)


async def gitlab_get_file(
    client: GitLabClient,
    project_id: int | str,
    file_path: str,
    ref: str,
) -> ToolResponse:
    """读取指定分支、标签或提交中的仓库文件。"""

    logger.info("MCP tool request tool=gitlab_get_file")
    if error := validate_project_id(project_id):
        return parameter_error(error)
    if error := validate_non_empty(file_path, "file_path"):
        return parameter_error(error)
    if error := validate_non_empty(ref, "ref"):
        return parameter_error(error)

    try:
        payload = await client.get_file(project_id, file_path, ref)
        repository_file = RepositoryFile.model_validate(payload)
    except GitLabClientError as exc:
        return client_error_response(exc)
    except ValidationError as exc:
        return response_validation_error(exc)
    return success_response(repository_file.model_dump(mode="json"))


async def gitlab_list_files(
    client: GitLabClient,
    project_id: int | str,
    path: str = "",
    ref: str | None = None,
    recursive: bool = False,
) -> ToolResponse:
    """列出仓库目录内容，可选择递归读取全部分页。"""

    logger.info("MCP tool request tool=gitlab_list_files")
    if error := validate_project_id(project_id):
        return parameter_error(error)
    if ref is not None and (error := validate_non_empty(ref, "ref")):
        return parameter_error(error)

    try:
        payload = await client.list_files(
            project_id,
            path=path,
            ref=ref,
            recursive=recursive,
        )
        items = [RepositoryTreeItem.model_validate(item) for item in payload]
    except GitLabClientError as exc:
        return client_error_response(exc)
    except ValidationError as exc:
        return response_validation_error(exc)
    return success_response([item.model_dump(mode="json") for item in items])
