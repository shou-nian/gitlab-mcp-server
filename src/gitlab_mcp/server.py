"""GitLab MCP Server 定义。"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations

from gitlab_mcp.config import Settings
from gitlab_mcp.gitlab.client import GitLabClient
from gitlab_mcp.tools.merge_request import gitlab_get_merge_request
from gitlab_mcp.tools.project import gitlab_get_project
from gitlab_mcp.tools.repository import gitlab_get_file, gitlab_list_files
from gitlab_mcp.utils.logger import get_logger

logger = get_logger(__name__)

READ_ONLY_ANNOTATIONS = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=True,
)


@dataclass
class AppContext:
    """MCP Server 生命周期内共享的依赖。"""

    gitlab_client: GitLabClient


def create_server(
    *,
    settings: Settings | None = None,
    client: GitLabClient | None = None,
) -> FastMCP:
    """创建并注册全部只读 Tool。

    测试可以注入 Client；生产环境则由 lifespan 创建并关闭连接池。
    """

    lifespan = None if client is not None else _create_lifespan(settings)
    server = FastMCP(
        name="gitlab-mcp-server",
        instructions="通过只读 Tool 查询 GitLab 项目、仓库文件和 Merge Request。",
        lifespan=lifespan,
    )

    def resolve_client(context: Context) -> GitLabClient:
        if client is not None:
            return client
        app_context = context.request_context.lifespan_context
        if not isinstance(app_context, AppContext):
            raise RuntimeError("GitLab Client 尚未初始化")
        return app_context.gitlab_client

    @server.tool(
        name="gitlab_get_project",
        description=(
            "获取 GitLab 项目信息。project_id 可使用正整数 ID，"
            "也可使用 namespace/project 项目路径。"
        ),
        annotations=READ_ONLY_ANNOTATIONS,
        structured_output=True,
    )
    async def get_project(project_id: int | str, context: Context) -> dict[str, Any]:
        return await gitlab_get_project(resolve_client(context), project_id)

    @server.tool(
        name="gitlab_get_file",
        description=(
            "读取 GitLab 仓库文件及元数据。ref 必须是分支、标签或提交 SHA；"
            "GitLab 返回的文件 content 通常使用 base64 编码。"
        ),
        annotations=READ_ONLY_ANNOTATIONS,
        structured_output=True,
    )
    async def get_file(
        project_id: int | str,
        file_path: str,
        ref: str,
        context: Context,
    ) -> dict[str, Any]:
        return await gitlab_get_file(resolve_client(context), project_id, file_path, ref)

    @server.tool(
        name="gitlab_list_files",
        description=(
            "列出 GitLab 仓库目录内容。path 为空时列出仓库根目录；"
            "recursive=true 时递归返回全部分页结果。"
        ),
        annotations=READ_ONLY_ANNOTATIONS,
        structured_output=True,
    )
    async def list_files(
        project_id: int | str,
        context: Context,
        path: str = "",
        ref: str | None = None,
        recursive: bool = False,
    ) -> dict[str, Any]:
        return await gitlab_list_files(
            resolve_client(context),
            project_id,
            path,
            ref,
            recursive,
        )

    @server.tool(
        name="gitlab_get_merge_request",
        description=(
            "获取 GitLab Merge Request 信息。merge_request_iid 是项目内显示的 MR IID，"
            "不是全局数据库 ID。"
        ),
        annotations=READ_ONLY_ANNOTATIONS,
        structured_output=True,
    )
    async def get_merge_request(
        project_id: int | str,
        merge_request_iid: int,
        context: Context,
    ) -> dict[str, Any]:
        return await gitlab_get_merge_request(
            resolve_client(context),
            project_id,
            merge_request_iid,
        )

    return server


def _create_lifespan(settings: Settings | None):
    @asynccontextmanager
    async def lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
        del server
        resolved_settings = settings or Settings()
        logger.info("GitLab MCP Server lifespan started")
        async with GitLabClient(resolved_settings) as gitlab_client:
            yield AppContext(gitlab_client=gitlab_client)
        logger.info("GitLab MCP Server lifespan stopped")

    return lifespan
