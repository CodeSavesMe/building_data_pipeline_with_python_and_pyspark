from __future__ import annotations

import json
from dataclasses import dataclass

from paccafe_pipeline.core.contracts import PipelineJob
from paccafe_pipeline.core.logging import get_logger
from paccafe_pipeline.infrastructure.database import DatabaseClient
from paccafe_pipeline.infrastructure.log_repository import PipelineLogRepository
from paccafe_pipeline.infrastructure.object_storage import FailedDataPayload, ObjectStorageClient
from paccafe_pipeline.domain.entities import BatchContext

logger = get_logger(__name__)


@dataclass
class WarehouseStagingSyncJob(PipelineJob):
    """Copy staging tables into a transient warehouse schema for SQL transforms."""

    name: str
    tables: list[str]
    staging_database: DatabaseClient
    warehouse_database: DatabaseClient
    log_repository: PipelineLogRepository
    failed_data_storage: ObjectStorageClient
    batch_context: BatchContext
    source_schema: str = "public"
    target_schema: str = "etl_staging"

    def run(self) -> None:
        logger.info("Starting warehouse staging sync job %s", self.name)
        self.log_repository.log(step="warehouse", component=self.name, status="STARTED")

        try:
            self.warehouse_database.create_schema(self.target_schema)
            for table in self.tables:
                columns = self.staging_database.describe_columns(table, schema=self.source_schema)
                column_names = [column["column_name"] for column in columns]
                self.warehouse_database.drop_table_if_exists(table, schema=self.target_schema)
                self.warehouse_database.create_table_from_columns(table, columns, schema=self.target_schema)
                column_sql = ", ".join(f'"{column}"' for column in column_names)
                row_count = self.staging_database.copy_query_to_table(
                    query=f"SELECT {column_sql} FROM public.\"{table}\"",
                    target=self.warehouse_database,
                    target_table=table,
                    target_columns=column_names,
                    target_schema=self.target_schema,
                )
                logger.info("Synced %s rows into %s.%s", row_count, self.target_schema, table)
                self.log_repository.log(
                    step="warehouse",
                    component=f"{self.name}:{table}",
                    status="SUCCESS",
                    table_name=table,
                    error_msg=f"row_count={row_count}",
                )

            self.log_repository.log(step="warehouse", component=self.name, status="SUCCESS")
        except Exception as exc:
            dump_path = self.failed_data_storage.dump_failed_data(
                FailedDataPayload(
                    layer="warehouse",
                    job_name=self.name,
                    batch_id=self.batch_context.batch_id,
                    data={"tables": self.tables, "target_schema": self.target_schema},
                    error_message=str(exc),
                )
            )
            logger.exception("Warehouse staging sync failed; dumped failure payload to %s", dump_path)
            self.log_repository.log(
                step="warehouse",
                component=self.name,
                status="FAILED",
                error_msg=f"{exc}; failed_data={dump_path}",
            )
            raise


@dataclass
class WarehouseSqlJob(PipelineJob):
    """Run warehouse transformation SQL."""

    name: str
    sql: str
    warehouse_database: DatabaseClient
    log_repository: PipelineLogRepository
    failed_data_storage: ObjectStorageClient
    batch_context: BatchContext
    summary_query: str | None = None

    def run(self) -> None:
        logger.info("Starting warehouse job %s", self.name)
        self.log_repository.log(step="warehouse", component=self.name, status="STARTED")

        try:
            self.warehouse_database.execute(self.sql)
            summary = self.warehouse_database.fetch_dicts(self.summary_query) if self.summary_query else []
            logger.info("Finished warehouse job %s", self.name)
            self.log_repository.log(
                step="warehouse",
                component=self.name,
                status="SUCCESS",
                error_msg=json.dumps(summary),
            )
        except Exception as exc:
            dump_path = self.failed_data_storage.dump_failed_data(
                FailedDataPayload(
                    layer="warehouse",
                    job_name=self.name,
                    batch_id=self.batch_context.batch_id,
                    data={"sql_preview": self.sql[:1000]},
                    error_message=str(exc),
                )
            )
            logger.exception("Warehouse SQL job %s failed; dumped failure payload to %s", self.name, dump_path)
            self.log_repository.log(
                step="warehouse",
                component=self.name,
                status="FAILED",
                error_msg=f"{exc}; failed_data={dump_path}",
            )
            raise


@dataclass
class WarehousePipeline(PipelineJob):
    """Run all staging-to-warehouse jobs."""

    name: str
    jobs: list[PipelineJob]

    def run(self) -> None:
        logger.info("Starting warehouse pipeline")
        for job in self.jobs:
            job.run()
        logger.info("Finished warehouse pipeline")
