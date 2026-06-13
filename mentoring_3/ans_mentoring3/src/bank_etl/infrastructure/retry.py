from collections.abc import Callable
from dataclasses import dataclass
from time import sleep
from typing import TypeVar

from loguru import logger

from bank_etl.infrastructure.config import RetrySettings

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    settings: RetrySettings

    def execute(self, operation: Callable[[], T], operation_name: str) -> T:
        delay = self.settings.initial_delay_seconds

        for attempt in range(1, self.settings.attempts + 1):
            try:
                return operation()
            except Exception as error:
                if attempt == self.settings.attempts:
                    logger.exception(
                        "Operation '{}' failed after {} attempts",
                        operation_name,
                        attempt,
                    )
                    raise

                logger.warning(
                    "Operation '{}' failed on attempt {}/{}: {}. Retrying in {:.1f}s",
                    operation_name,
                    attempt,
                    self.settings.attempts,
                    error,
                    delay,
                )
                sleep(delay)
                delay = min(delay * 2, self.settings.maximum_delay_seconds)

        raise RuntimeError("Retry loop ended unexpectedly")
