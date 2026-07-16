"""Merge Request Tool 测试。"""

import asyncio
from unittest.mock import AsyncMock

from gitlab_mcp.gitlab.client import GitLabClient
from gitlab_mcp.tools.merge_request import gitlab_get_merge_request


def test_get_merge_request_returns_validated_json() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)
        client.get_merge_request.return_value = {
            "id": 101,
            "iid": 7,
            "project_id": 1,
            "title": "Add MCP server",
            "state": "opened",
            "source_branch": "feature/mcp",
            "target_branch": "main",
            "web_url": "https://gitlab.example.com/group/demo/-/merge_requests/7",
            "author": {"id": 2, "username": "developer"},
        }

        result = await gitlab_get_merge_request(client, 1, 7)

        client.get_merge_request.assert_awaited_once_with(1, 7)
        assert result["success"] is True
        assert result["data"]["iid"] == 7

    asyncio.run(run())


def test_get_merge_request_rejects_non_positive_iid() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)

        result = await gitlab_get_merge_request(client, 1, 0)

        client.get_merge_request.assert_not_awaited()
        assert result == {
            "success": False,
            "error": {
                "type": "invalid_parameters",
                "message": "merge_request_iid 必须是正整数",
            },
        }

    asyncio.run(run())
