"""GitLabClient 测试。"""

import asyncio

import httpx

from gitlab_mcp.config import Settings
from gitlab_mcp.gitlab.client import GitLabClient, GitLabClientError


def _settings() -> Settings:
    return Settings(
        gitlab_url="https://gitlab.example.com",
        gitlab_token="test-token",
        _env_file=None,
    )


def test_get_file_encodes_paths_and_sends_authentication() -> None:
    async def run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            encoded_path = request.url.raw_path.split(b"?", maxsplit=1)[0]
            assert encoded_path == (b"/api/v4/projects/group%2Frepo/repository/files/src%2Fapp.py")
            assert request.url.params["ref"] == "feature/test"
            assert request.headers["private-token"] == "test-token"
            return httpx.Response(200, json={"file_name": "app.py"})

        http_client = httpx.AsyncClient(
            base_url="https://gitlab.example.com/api/v4",
            transport=httpx.MockTransport(handler),
            headers={"PRIVATE-TOKEN": "test-token"},
        )
        client = GitLabClient(_settings(), http_client=http_client)
        try:
            result = await client.get_file("group/repo", "src/app.py", "feature/test")
        finally:
            await http_client.aclose()

        assert result == {"file_name": "app.py"}

    asyncio.run(run())


def test_list_files_collects_all_pages() -> None:
    async def run() -> None:
        requested_pages: list[str] = []

        def handler(request: httpx.Request) -> httpx.Response:
            requested_pages.append(request.url.params["page"])
            if request.url.params["page"] == "1":
                return httpx.Response(
                    200,
                    headers={"X-Next-Page": "2"},
                    json=[{"name": "src"}],
                )
            return httpx.Response(200, json=[{"name": "README.md"}])

        http_client = httpx.AsyncClient(
            base_url="https://gitlab.example.com/api/v4",
            transport=httpx.MockTransport(handler),
        )
        client = GitLabClient(_settings(), http_client=http_client)
        try:
            result = await client.list_files(1, path="", ref="main", recursive=True)
        finally:
            await http_client.aclose()

        assert requested_pages == ["1", "2"]
        assert result == [{"name": "src"}, {"name": "README.md"}]

    asyncio.run(run())


def test_http_error_is_converted_to_structured_error() -> None:
    async def run() -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(404, json={"message": "404 Project Not Found"})

        http_client = httpx.AsyncClient(
            base_url="https://gitlab.example.com/api/v4",
            transport=httpx.MockTransport(handler),
        )
        client = GitLabClient(_settings(), http_client=http_client)
        try:
            try:
                await client.get_project(999)
            except GitLabClientError as exc:
                assert exc.to_dict() == {
                    "message": "GitLab API 请求失败",
                    "status_code": 404,
                    "details": {"message": "404 Project Not Found"},
                }
            else:
                raise AssertionError("应抛出 GitLabClientError")
        finally:
            await http_client.aclose()

    asyncio.run(run())
