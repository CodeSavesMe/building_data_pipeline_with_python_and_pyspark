from dataclasses import dataclass

from loguru import logger
from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession

from bank_etl.domain.models import SourceTable
from bank_etl.infrastructure.config import DatabaseSettings
from bank_etl.infrastructure.retry import RetryPolicy
from bank_etl.ports.readers import SourceDatabaseReader


@dataclass
class PostgresJdbcReader(SourceDatabaseReader):
    spark: SparkSession
    database: DatabaseSettings
    retry_policy: RetryPolicy

    def read_table(self, table: SourceTable) -> DataFrame:
        return self.retry_policy.execute(
            lambda: self._read_and_materialize(table),
            f"extract source table {table.value}",
        )

    def _read_and_materialize(self, table: SourceTable) -> DataFrame:
        logger.info("Extracting PostgreSQL table {}", table.value)
        frame: DataFrame | None = None
        try:
            options = self.database.jdbc_options | {
                "dbtable": f"public.{table.value}",
                "fetchsize": "10000",
            }
            frame = self.spark.read.format("jdbc").options(**options).load()
            frame.persist(StorageLevel.MEMORY_AND_DISK)
            row_count = frame.count()
            logger.info("Extracted {} rows from {}", row_count, table.value)
            return frame
        except Exception:
            if frame is not None:
                frame.unpersist(blocking=False)
            raise
