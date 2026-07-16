"""命令行入口与优雅退出测试。"""

import asyncio
import signal
from unittest.mock import Mock

from gitlab_mcp import main as main_module


def test_run_server_cancels_server_after_shutdown_signal(monkeypatch) -> None:
    async def run() -> None:
        handlers = {}
        stopped = asyncio.Event()

        def install_handler(shutdown_signal, handler):
            handlers.setdefault(shutdown_signal, handler)
            return signal.SIG_DFL

        monkeypatch.setattr(main_module.signal, "signal", install_handler)
        monkeypatch.setattr(main_module.signal, "getsignal", lambda shutdown_signal: signal.SIG_DFL)

        class FakeServer:
            async def run_stdio_async(self) -> None:
                handlers[signal.SIGTERM](signal.SIGTERM, None)
                try:
                    await asyncio.Event().wait()
                finally:
                    stopped.set()

        await main_module.run_server(FakeServer())

        assert stopped.is_set()

    asyncio.run(run())


def test_main_swallows_keyboard_interrupt_and_finishes_logging(monkeypatch) -> None:
    settings = Mock(log_level="INFO")
    server = Mock()
    log_messages: list[str] = []

    monkeypatch.setattr(main_module, "Settings", Mock(return_value=settings))
    monkeypatch.setattr(main_module, "configure_logging", Mock())
    monkeypatch.setattr(main_module, "create_server", Mock(return_value=server))
    monkeypatch.setattr(main_module, "run_server", Mock(return_value=None))
    monkeypatch.setattr(
        main_module.asyncio,
        "run",
        Mock(side_effect=KeyboardInterrupt),
    )
    monkeypatch.setattr(
        main_module.logger,
        "info",
        lambda message, *args: log_messages.append(message % args if args else message),
    )

    main_module.main()

    assert log_messages[-2:] == [
        "Stopping GitLab MCP Server signal=SIGINT",
        "GitLab MCP Server stopped",
    ]
