from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class PipelineJob(ABC):
    """Base contract for executable pipeline jobs."""

    name: str

    @abstractmethod
    def run(self) -> None:
        """Execute the job."""


class DataSource(Protocol):
    """Contract for source adapters."""

    def extract(self) -> Any:
        """Extract data from the source."""


class DataTransformer(Protocol):
    """Contract for transformation services."""

    def transform(self, data: Any) -> Any:
        """Transform extracted or staged data."""


class DataSink(Protocol):
    """Contract for sink adapters."""

    def load(self, data: Any) -> None:
        """Load data into a sink."""
