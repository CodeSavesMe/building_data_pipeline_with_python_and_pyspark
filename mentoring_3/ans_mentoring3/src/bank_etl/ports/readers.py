from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from bank_etl.domain.models import SourceTable


class SourceDatabaseReader(ABC):
    @abstractmethod
    def read_table(self, table: SourceTable) -> Any:
        """Read and materialize one source database table."""


class SourceFileReader(ABC):
    @abstractmethod
    def read_csv(self, path: Path) -> Any:
        """Read and materialize a CSV file or Spark CSV directory."""
