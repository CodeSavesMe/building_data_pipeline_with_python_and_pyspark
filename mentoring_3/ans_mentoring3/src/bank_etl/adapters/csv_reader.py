from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from pyspark import StorageLevel
from pyspark.sql import DataFrame, SparkSession

from bank_etl.infrastructure.retry import RetryPolicy
from bank_etl.ports.readers import SourceFileReader


@dataclass
class SparkCsvReader(SourceFileReader):
    spark: SparkSession
    retry_policy: RetryPolicy

    def read_csv(self, path: Path) -> DataFrame:
        return self.retry_policy.execute(
            lambda: self._read_and_materialize(path),
            f"extract CSV {path}",
        )

    def _read_and_materialize(self, path: Path) -> DataFrame:
        if not path.exists():
            raise FileNotFoundError(f"CSV source not found: {path}")

        logger.info("Extracting CSV source {}", path)
        frame: DataFrame | None = None
        try:
            frame = (
                self.spark.read.option("header", True)
                .option("inferSchema", False)
                .option("mode", "FAILFAST")
                .csv(str(path))
            )
            frame.persist(StorageLevel.MEMORY_AND_DISK)
            row_count = frame.count()
            logger.info("Extracted {} rows from CSV source", row_count)
            return frame
        except Exception:
            if frame is not None:
                frame.unpersist(blocking=False)
            raise
