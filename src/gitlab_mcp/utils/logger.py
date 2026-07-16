"""日志配置。"""

import logging
import sys

_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"


def configure_logging(level: str = "INFO") -> None:
    """配置写入 stderr 的统一日志，避免污染 MCP stdio 输出。"""

    normalized_level = level.upper()
    if normalized_level not in logging.getLevelNamesMapping():
        normalized_level = "INFO"

    logging.basicConfig(
        level=normalized_level,
        format=_LOG_FORMAT,
        stream=sys.stderr,
    )


def get_logger(name: str) -> logging.Logger:
    """获取模块 logger。"""

    return logging.getLogger(name)
