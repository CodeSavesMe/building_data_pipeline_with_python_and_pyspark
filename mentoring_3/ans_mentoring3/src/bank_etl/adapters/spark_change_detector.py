from dataclasses import dataclass

import psycopg2
from loguru import logger
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

from bank_etl.domain.models import (
    TARGET_KEY_COLUMNS,
    ChangeSummary,
    TargetDataset,
    WarehouseData,
)
from bank_etl.infrastructure.config import DatabaseSettings
from bank_etl.infrastructure.retry import RetryPolicy
from bank_etl.ports.profiling import ChangeDetector


@dataclass
class SparkBatchChangeDetector(ChangeDetector):
    spark: SparkSession
    database: DatabaseSettings
    retry_policy: RetryPolicy

    def detect(self, data: WarehouseData) -> tuple[ChangeSummary, ...]:
        logger.info("Semi-CDC snapshot comparison started")
        changes = tuple(
            self.retry_policy.execute(
                lambda dataset=dataset: self._detect_dataset(dataset),
                f"detect changes for {dataset.table.value}",
            )
            for dataset in data.datasets
        )
        logger.info("Semi-CDC snapshot comparison completed")
        return changes

    def _detect_dataset(self, dataset: TargetDataset) -> ChangeSummary:
        previous_count = self._table_row_count(dataset.table.value)
        if previous_count == 0:
            summary = ChangeSummary(dataset.table, dataset.row_count, 0, 0, 0)
            self._log_summary(summary)
            return summary

        key_columns = TARGET_KEY_COLUMNS[dataset.table]
        previous = self._read_existing(dataset)
        current_hashes = self._with_hash(dataset.frame, key_columns).select(
            *key_columns,
            F.col("_row_hash").alias("_current_hash"),
            F.lit(1).alias("_current_exists"),
        )
        previous_hashes = self._with_hash(previous, key_columns).select(
            *key_columns,
            F.col("_row_hash").alias("_previous_hash"),
            F.lit(1).alias("_previous_exists"),
        )
        joined = current_hashes.join(previous_hashes, list(key_columns), "full_outer")
        metrics = joined.agg(
            F.sum(F.when(F.col("_previous_exists").isNull(), 1).otherwise(0)).alias("inserted"),
            F.sum(F.when(F.col("_current_exists").isNull(), 1).otherwise(0)).alias("deleted"),
            F.sum(
                F.when(
                    F.col("_current_exists").isNotNull()
                    & F.col("_previous_exists").isNotNull()
                    & (F.col("_current_hash") != F.col("_previous_hash")),
                    1,
                ).otherwise(0)
            ).alias("updated"),
            F.sum(
                F.when(
                    F.col("_current_exists").isNotNull()
                    & F.col("_previous_exists").isNotNull()
                    & (F.col("_current_hash") == F.col("_previous_hash")),
                    1,
                ).otherwise(0)
            ).alias("unchanged"),
        ).first()
        summary = ChangeSummary(
            table=dataset.table,
            inserted_count=int(metrics["inserted"] or 0),
            updated_count=int(metrics["updated"] or 0),
            deleted_count=int(metrics["deleted"] or 0),
            unchanged_count=int(metrics["unchanged"] or 0),
        )
        self._log_summary(summary)
        return summary

    def _read_existing(self, dataset: TargetDataset) -> DataFrame:
        columns = ", ".join(self._quote(column) for column in dataset.frame.columns)
        query = f'(SELECT {columns} FROM public."{dataset.table.value}") AS snapshot'
        options = self.database.jdbc_options | {
            "dbtable": query,
            "fetchsize": "10000",
        }
        return self.spark.read.format("jdbc").options(**options).load()

    def _table_row_count(self, table_name: str) -> int:
        with psycopg2.connect(**self.database.psycopg_options) as connection:
            with connection.cursor() as cursor:
                cursor.execute(f'SELECT COUNT(*) FROM public."{table_name}"')
                return int(cursor.fetchone()[0])

    @staticmethod
    def _with_hash(frame: DataFrame, key_columns: tuple[str, ...]) -> DataFrame:
        payload_columns = [column for column in frame.columns if column not in key_columns]
        payload = F.struct(*(F.col(column).alias(column) for column in payload_columns))
        return frame.select(
            *key_columns,
            F.sha2(
                F.to_json(payload, options={"ignoreNullFields": "false"}),
                256,
            ).alias("_row_hash"),
        )

    @staticmethod
    def _quote(identifier: str) -> str:
        return f'"{identifier.replace(chr(34), chr(34) * 2)}"'

    @staticmethod
    def _log_summary(summary: ChangeSummary) -> None:
        logger.info(
            "Semi-CDC {}: inserted={}, updated={}, deleted={}, unchanged={}",
            summary.table.value,
            summary.inserted_count,
            summary.updated_count,
            summary.deleted_count,
            summary.unchanged_count,
        )
