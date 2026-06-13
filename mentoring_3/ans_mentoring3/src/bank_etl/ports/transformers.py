from abc import ABC, abstractmethod

from bank_etl.domain.models import SourceData, WarehouseData


class DataTransformer(ABC):
    @abstractmethod
    def transform(self, source: SourceData) -> WarehouseData:
        """Apply source-to-target mapping and data quality rules."""
