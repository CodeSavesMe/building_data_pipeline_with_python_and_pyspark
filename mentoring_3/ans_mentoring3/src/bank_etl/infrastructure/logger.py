import logging
import sys
from pathlib import Path
from types import FrameType

from loguru import logger


class InterceptHandler(logging.Handler):
    """Route standard Python and Py4J logging records through Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logger(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    log_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}"
    )
    logger.add(
        sys.stderr,
        level="INFO",
        format=log_format,
        backtrace=True,
        diagnose=False,
        enqueue=True,
    )
    logger.add(
        log_path,
        level="DEBUG",
        format=log_format,
        rotation="25 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=False,
        enqueue=True,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
    for name in ("py4j", "py4j.java_gateway", "pyspark"):
        logging.getLogger(name).setLevel(logging.WARNING)

    logger.info("Centralized logging initialized at {}", log_path)


def shutdown_logger() -> None:
    """Drain queued Loguru messages before the process exits."""
    logger.complete()
    logger.remove()
