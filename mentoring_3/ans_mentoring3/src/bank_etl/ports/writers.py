from abc import ABC, abstractmethod

from bank_etl.domain.models import WarehouseData


class WarehouseWriter(ABC):
    @abstractmethod
    def replace_all(self, data: WarehouseData) -> None:
        """Replace all warehouse target tables with the supplied datasets."""
