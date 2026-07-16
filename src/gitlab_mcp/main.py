"""GitLab MCP Server 命令行入口。"""

from gitlab_mcp.config import Settings
from gitlab_mcp.server import create_server
from gitlab_mcp.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)


def main() -> None:
    """通过 stdio 启动 MCP Server。"""

    settings = Settings()
    configure_logging(settings.log_level)
    logger.info("Starting GitLab MCP Server transport=stdio")
    create_server(settings=settings).run(transport="stdio")


if __name__ == "__main__":
    main()
