"""GitLab MCP Server 命令行入口。"""

import asyncio
import signal
from collections.abc import Callable
from types import FrameType

from mcp.server.fastmcp import FastMCP

from gitlab_mcp.config import Settings
from gitlab_mcp.server import create_server
from gitlab_mcp.utils.logger import configure_logging, get_logger

logger = get_logger(__name__)

SignalHandler = signal.Handlers | Callable[[int, FrameType | None], None]


async def run_server(server: FastMCP) -> None:
    """运行 stdio Server，并在退出信号到达后等待生命周期清理完成。"""

    shutdown_event = asyncio.Event()
    registered_handlers: list[tuple[signal.Signals, SignalHandler]] = []

    def request_shutdown(signum: int, frame: FrameType | None) -> None:
        del frame
        if not shutdown_event.is_set():
            logger.info("Stopping GitLab MCP Server signal=%s", signal.Signals(signum).name)
            shutdown_event.set()

    for shutdown_signal in (signal.SIGINT, signal.SIGTERM):
        previous_handler = signal.getsignal(shutdown_signal)
        try:
            signal.signal(shutdown_signal, request_shutdown)
        except (OSError, ValueError):
            # signal.signal 只能在主线程调用；非 CLI 嵌入场景仍可通过任务取消退出。
            continue
        registered_handlers.append((shutdown_signal, previous_handler))

    server_task = asyncio.create_task(server.run_stdio_async())
    shutdown_task = asyncio.create_task(shutdown_event.wait())
    try:
        done, _ = await asyncio.wait(
            {server_task, shutdown_task},
            return_when=asyncio.FIRST_COMPLETED,
        )
        if shutdown_task in done:
            server_task.cancel()

        try:
            await server_task
        except asyncio.CancelledError:
            if not shutdown_event.is_set():
                raise
    finally:
        for task in (server_task, shutdown_task):
            if not task.done():
                task.cancel()
        await asyncio.gather(server_task, shutdown_task, return_exceptions=True)
        for shutdown_signal, previous_handler in reversed(registered_handlers):
            signal.signal(shutdown_signal, previous_handler)


def main() -> None:
    """通过 stdio 启动 MCP Server。"""

    settings = Settings()
    configure_logging(settings.log_level)
    logger.info("Starting GitLab MCP Server transport=stdio")
    server = create_server(settings=settings)
    try:
        asyncio.run(run_server(server))
    except KeyboardInterrupt:
        # 覆盖信号处理器尚未安装或连续中断的极小时间窗，避免输出 traceback。
        logger.info("Stopping GitLab MCP Server signal=SIGINT")
    finally:
        logger.info("GitLab MCP Server stopped")


if __name__ == "__main__":
    main()
