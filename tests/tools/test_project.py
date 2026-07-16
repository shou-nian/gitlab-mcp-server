"""项目 Tool 测试。"""

import asyncio
from unittest.mock import AsyncMock

from gitlab_mcp.gitlab.client import GitLabClient, GitLabClientError
from gitlab_mcp.tools.project import gitlab_get_project


def test_get_project_returns_validated_json() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)
        client.get_project.return_value = {
            "id": 1,
            "name": "demo",
            "path_with_namespace": "group/demo",
            "web_url": "https://gitlab.example.com/group/demo",
            "default_branch": "main",
            "extra_field": "preserved",
        }

        result = await gitlab_get_project(client, "group/demo")

        client.get_project.assert_awaited_once_with("group/demo")
        assert result["success"] is True
        assert result["data"]["id"] == 1
        assert result["data"]["extra_field"] == "preserved"

    asyncio.run(run())


def test_get_project_rejects_invalid_project_id() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)

        result = await gitlab_get_project(client, "  ")

        client.get_project.assert_not_awaited()
        assert result == {
            "success": False,
            "error": {"type": "invalid_parameters", "message": "project_id 不能为空"},
        }

    asyncio.run(run())


def test_get_project_returns_structured_client_error() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)
        client.get_project.side_effect = GitLabClientError(
            "GitLab API 请求失败",
            status_code=403,
        )

        result = await gitlab_get_project(client, 1)

        assert result == {
            "success": False,
            "error": {
                "type": "gitlab_error",
                "message": "GitLab API 请求失败",
                "status_code": 403,
            },
        }

    asyncio.run(run())
