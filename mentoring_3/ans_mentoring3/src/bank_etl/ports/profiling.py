from abc import ABC, abstractmethod

from bank_etl.domain.models import (
    ChangeSummary,
    DataProfile,
    ProfileInput,
    ProfileStage,
    WarehouseData,
)


class DataProfiler(ABC):
    @abstractmethod
    def profile(
        self,
        datasets: tuple[ProfileInput, ...],
        stage: ProfileStage,
    ) -> tuple[DataProfile, ...]:
        """Collect row, column, null, and duplicate-key metrics."""


class ChangeDetector(ABC):
    @abstractmethod
    def detect(self, data: WarehouseData) -> tuple[ChangeSummary, ...]:
        """Compare the transformed batch with the current warehouse snapshot."""
