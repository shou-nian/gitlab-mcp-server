"""真实 stdio MCP 进程集成测试。"""

import asyncio
import shutil
import tempfile
from datetime import timedelta

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def test_stdio_server_supports_discovery_and_safe_tool_call() -> None:
    """启动真实子进程；无效参数在 Tool 层返回，不访问 GitLab。"""

    async def run() -> None:
        command = shutil.which("gitlab-mcp")
        assert command is not None
        parameters = StdioServerParameters(
            command=command,
            env={
                "GITLAB_URL": "https://gitlab.example.com",
                "GITLAB_TOKEN": "test-token",
                "LOG_LEVEL": "CRITICAL",
            },
        )
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as error_log:
            async with stdio_client(parameters, errlog=error_log) as (
                read_stream,
                write_stream,
            ):
                async with ClientSession(
                    read_stream,
                    write_stream,
                    read_timeout_seconds=timedelta(seconds=10),
                ) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    result = await session.call_tool(
                        "gitlab_get_project",
                        {"project_id": ""},
                    )

        assert {tool.name for tool in tools.tools} == {
            "gitlab_get_project",
            "gitlab_get_file",
            "gitlab_list_files",
            "gitlab_get_merge_request",
        }
        assert result.isError is False
        assert result.structuredContent == {
            "success": False,
            "error": {
                "type": "invalid_parameters",
                "message": "project_id 不能为空",
            },
        }

    asyncio.run(run())
