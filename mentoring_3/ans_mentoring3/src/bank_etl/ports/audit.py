from abc import ABC, abstractmethod
from pathlib import Path

from bank_etl.domain.models import ChangeSummary, DataProfile


class RunAuditRepository(ABC):
    @abstractmethod
    def start_run(self) -> str:
        """Create and return a pipeline run identifier."""

    @abstractmethod
    def save_profiles(self, run_id: str, profiles: tuple[DataProfile, ...]) -> None:
        """Persist source or target profiles for a run."""

    @abstractmethod
    def save_changes(self, run_id: str, changes: tuple[ChangeSummary, ...]) -> None:
        """Persist batch change detection results."""

    @abstractmethod
    def mark_succeeded(self, run_id: str, duration_seconds: float) -> None:
        """Mark a pipeline run successful."""

    @abstractmethod
    def mark_failed(self, run_id: str, error_message: str) -> None:
        """Mark a pipeline run failed."""

    @abstractmethod
    def export_summary(self, run_id: str, path: Path) -> None:
        """Export a machine-readable summary for the latest run."""
