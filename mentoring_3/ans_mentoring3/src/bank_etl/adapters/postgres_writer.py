from dataclasses import dataclass

import psycopg2
from loguru import logger
from pyspark.sql import DataFrame

from bank_etl.domain.models import LOAD_ORDER, TargetDataset, WarehouseData
from bank_etl.infrastructure.config import DatabaseSettings
from bank_etl.infrastructure.retry import RetryPolicy
from bank_etl.ports.writers import WarehouseWriter


@dataclass
class PostgresWarehouseWriter(WarehouseWriter):
    database: DatabaseSettings
    retry_policy: RetryPolicy

    def replace_all(self, data: WarehouseData) -> None:
        # Retrying individual JDBC writes can duplicate rows after a partial failure.
        # Retrying the complete refresh is idempotent because every attempt truncates first.
        self.retry_policy.execute(
            lambda: self._replace_once(data),
            "replace all warehouse tables",
        )

    def _replace_once(self, data: WarehouseData) -> None:
        self._truncate_targets()
        for dataset in data.datasets:
            self._append(dataset)
        self._verify_counts(data)

    def _truncate_targets(self) -> None:
        table_names = ", ".join(f'public."{table.value}"' for table in reversed(LOAD_ORDER))
        statement = f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"
        logger.info("Truncating all warehouse target tables")
        with psycopg2.connect(**self.database.psycopg_options) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)
        logger.info("Warehouse target tables truncated")

    def _append(self, dataset: TargetDataset) -> None:
        logger.info(
            "Appending {} rows to warehouse table {}",
            dataset.row_count,
            dataset.table.value,
        )
        options = self.database.jdbc_options | {
            "dbtable": f"public.{dataset.table.value}",
            "batchsize": "10000",
            "isolationLevel": "READ_COMMITTED",
        }
        self._write_frame(dataset.frame, options)
        logger.info("Warehouse table {} loaded", dataset.table.value)

    @staticmethod
    def _write_frame(frame: DataFrame, options: dict[str, str]) -> None:
        frame.write.format("jdbc").options(**options).mode("append").save()

    def _verify_counts(self, data: WarehouseData) -> None:
        logger.info("Verifying warehouse row counts")
        with psycopg2.connect(**self.database.psycopg_options) as connection:
            with connection.cursor() as cursor:
                for dataset in data.datasets:
                    cursor.execute(f'SELECT COUNT(*) FROM public."{dataset.table.value}"')
                    actual_count = cursor.fetchone()[0]
                    if actual_count != dataset.row_count:
                        raise RuntimeError(
                            f"Row count mismatch for {dataset.table.value}: "
                            f"expected {dataset.row_count}, got {actual_count}"
                        )
                    logger.info(
                        "Verified {} rows in {}",
                        actual_count,
                        dataset.table.value,
                    )
