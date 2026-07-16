"""MCP Server 注册和调用测试。"""

import asyncio
from unittest.mock import AsyncMock

from gitlab_mcp.gitlab.client import GitLabClient
from gitlab_mcp.server import create_server


def test_server_exposes_exactly_four_read_only_tools() -> None:
    async def run() -> None:
        server = create_server(client=AsyncMock(spec=GitLabClient))

        tools = await server.list_tools()

        assert {tool.name for tool in tools} == {
            "gitlab_get_project",
            "gitlab_get_file",
            "gitlab_list_files",
            "gitlab_get_merge_request",
        }
        for tool in tools:
            assert tool.annotations is not None
            assert tool.annotations.readOnlyHint is True
            assert tool.annotations.destructiveHint is False
            assert "context" not in tool.inputSchema.get("properties", {})

    asyncio.run(run())


def test_registered_project_tool_can_be_called() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)
        client.get_project.return_value = {
            "id": 1,
            "name": "demo",
            "path_with_namespace": "group/demo",
            "web_url": "https://gitlab.example.com/group/demo",
        }
        server = create_server(client=client)

        result = await server.call_tool("gitlab_get_project", {"project_id": 1})

        client.get_project.assert_awaited_once_with(1)
        content, structured_content = result
        assert content
        assert structured_content["success"] is True
        assert structured_content["data"]["path_with_namespace"] == "group/demo"

    asyncio.run(run())
