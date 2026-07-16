"""仓库 Tool 测试。"""

import asyncio
from unittest.mock import AsyncMock

from gitlab_mcp.gitlab.client import GitLabClient
from gitlab_mcp.tools.repository import gitlab_get_file, gitlab_list_files


def test_get_file_returns_gitlab_file_json() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)
        client.get_file.return_value = {
            "file_name": "README.md",
            "file_path": "README.md",
            "size": 12,
            "encoding": "base64",
            "content": "IyBEZW1v",
            "ref": "main",
            "blob_id": "blob",
            "commit_id": "commit",
            "last_commit_id": "last-commit",
        }

        result = await gitlab_get_file(client, 1, "README.md", "main")

        client.get_file.assert_awaited_once_with(1, "README.md", "main")
        assert result["success"] is True
        assert result["data"]["content"] == "IyBEZW1v"

    asyncio.run(run())


def test_get_file_rejects_empty_ref() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)

        result = await gitlab_get_file(client, 1, "README.md", "")

        client.get_file.assert_not_awaited()
        assert result["error"]["type"] == "invalid_parameters"

    asyncio.run(run())


def test_list_files_returns_validated_tree_items() -> None:
    async def run() -> None:
        client = AsyncMock(spec=GitLabClient)
        client.list_files.return_value = [
            {"id": "tree-id", "name": "src", "type": "tree", "path": "src", "mode": "040000"},
            {
                "id": "blob-id",
                "name": "README.md",
                "type": "blob",
                "path": "README.md",
                "mode": "100644",
            },
        ]

        result = await gitlab_list_files(client, "group/demo", ref="main", recursive=True)

        client.list_files.assert_awaited_once_with(
            "group/demo",
            path="",
            ref="main",
            recursive=True,
        )
        assert result["success"] is True
        assert [item["name"] for item in result["data"]] == ["src", "README.md"]

    asyncio.run(run())
