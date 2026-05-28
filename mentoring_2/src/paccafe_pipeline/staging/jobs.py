from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from paccafe_pipeline.core.contracts import PipelineJob
from paccafe_pipeline.core.logging import get_logger
from paccafe_pipeline.domain.entities import BatchContext
from paccafe_pipeline.infrastructure.database import DatabaseClient
from paccafe_pipeline.infrastructure.log_repository import PipelineLogRepository
from paccafe_pipeline.infrastructure.object_storage import FailedDataPayload, ObjectStorageClient

logger = get_logger(__name__)


def read_store_branch_spreadsheet_copy(csv_path: Path) -> list[dict[str, str]]:
    """Read the copied store branch spreadsheet data from CSV."""

    rows: list[dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            created_at = datetime.strptime(row["created_at"], "%m/%d/%Y %H:%M:%S")
            rows.append(
                {
                    "store_id": row["store_id"],
                    "store_name": row["store_name"],
                    "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
    return rows


@dataclass
class SourceToStagingJob(PipelineJob):
    """Extract one source dataset and load it to one staging table."""

    name: str
    source_table: str
    staging_table: str
    source_database: DatabaseClient
    staging_database: DatabaseClient
    batch_context: BatchContext
    log_repository: PipelineLogRepository
    failed_data_storage: ObjectStorageClient
    schema: str = "public"

    def run(self) -> None:
        logger.info("Starting staging job %s from %s", self.name, self.source_table)
        self.log_repository.log(
            step="staging",
            component=self.name,
            status="STARTED",
            table_name=self.staging_table,
        )

        try:
            source_columns = self.source_database.list_columns(self.source_table, schema=self.schema)
            staging_columns = self.staging_database.list_columns(self.staging_table, schema=self.schema)
            common_columns = [column for column in source_columns if column in staging_columns]
            if not common_columns:
                raise ValueError(f"No common columns found for {self.source_table} -> {self.staging_table}")

            self.staging_database.truncate_table(self.staging_table, schema=self.schema)
            column_sql = ", ".join(f'"{column}"' for column in common_columns)
            row_count = self.source_database.copy_query_to_table(
                query=f"SELECT {column_sql} FROM public.\"{self.source_table}\"",
                target=self.staging_database,
                target_table=self.staging_table,
                target_columns=common_columns,
                target_schema=self.schema,
            )
            logger.info("Finished staging job %s with %s rows", self.name, row_count)
            self.log_repository.log(
                step="staging",
                component=self.name,
                status="SUCCESS",
                table_name=self.staging_table,
                error_msg=f"row_count={row_count}",
            )
        except Exception as exc:
            dump_path = self.failed_data_storage.dump_failed_data(
                FailedDataPayload(
                    layer="staging",
                    job_name=self.name,
                    batch_id=self.batch_context.batch_id,
                    data={"source_table": self.source_table, "staging_table": self.staging_table},
                    error_message=str(exc),
                )
            )
            logger.exception("Staging job %s failed; dumped failure payload to %s", self.name, dump_path)
            self.log_repository.log(
                step="staging",
                component=self.name,
                status="FAILED",
                table_name=self.staging_table,
                error_msg=f"{exc}; failed_data={dump_path}",
            )
            raise


@dataclass
class SpreadsheetCopyToStagingJob(PipelineJob):
    """Load copied spreadsheet data into a staging table."""

    name: str
    csv_path: Path
    staging_table: str
    staging_database: DatabaseClient
    batch_context: BatchContext
    log_repository: PipelineLogRepository
    failed_data_storage: ObjectStorageClient
    schema: str = "public"

    def run(self) -> None:
        logger.info("Starting spreadsheet staging job %s from %s", self.name, self.csv_path)
        self.log_repository.log(
            step="staging",
            component=self.name,
            status="STARTED",
            table_name=self.staging_table,
        )

        try:
            rows = read_store_branch_spreadsheet_copy(self.csv_path)
            columns = ["store_id", "store_name", "created_at"]
            self.staging_database.truncate_table(self.staging_table, schema=self.schema)
            row_count = self.staging_database.copy_rows(
                table_name=self.staging_table,
                rows=rows,
                schema=self.schema,
                columns=columns,
            )
            logger.info("Finished spreadsheet staging job %s with %s rows", self.name, row_count)
            self.log_repository.log(
                step="staging",
                component=self.name,
                status="SUCCESS",
                table_name=self.staging_table,
                error_msg=f"row_count={row_count}",
            )
        except Exception as exc:
            dump_path = self.failed_data_storage.dump_failed_data(
                FailedDataPayload(
                    layer="staging",
                    job_name=self.name,
                    batch_id=self.batch_context.batch_id,
                    data={"csv_path": str(self.csv_path), "staging_table": self.staging_table},
                    error_message=str(exc),
                )
            )
            logger.exception("Spreadsheet staging job %s failed; dumped failure payload to %s", self.name, dump_path)
            self.log_repository.log(
                step="staging",
                component=self.name,
                status="FAILED",
                table_name=self.staging_table,
                error_msg=f"{exc}; failed_data={dump_path}",
            )
            raise


@dataclass
class StagingPipeline(PipelineJob):
    """Run all source-to-staging jobs."""

    name: str
    jobs: list[PipelineJob]

    def run(self) -> None:
        logger.info("Starting staging pipeline")
        for job in self.jobs:
            job.run()
        logger.info("Finished staging pipeline")
