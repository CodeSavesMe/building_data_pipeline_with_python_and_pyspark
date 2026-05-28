from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from paccafe_pipeline.config import PipelineSettings
from paccafe_pipeline.core.contracts import PipelineJob
from paccafe_pipeline.core.logging import configure_logging, get_logger
from paccafe_pipeline.domain import BatchContext
from paccafe_pipeline.infrastructure.database import DatabaseClient
from paccafe_pipeline.infrastructure.log_repository import PipelineLogRepository
from paccafe_pipeline.infrastructure.object_storage import MinioObjectStorageClient
from paccafe_pipeline.staging import SpreadsheetCopyToStagingJob, SourceToStagingJob, StagingPipeline
from paccafe_pipeline.warehouse import WarehousePipeline, WarehouseSqlJob, WarehouseStagingSyncJob
from paccafe_pipeline.warehouse.sql import LOAD_WAREHOUSE_SQL

logger = get_logger(__name__)

SOURCE_TABLES = [
    "customers",
    "employees",
    "orders",
    "order_details",
    "products",
    "inventory_tracking",
]

STAGING_TABLES = [
    *SOURCE_TABLES,
    "store_branch",
]

WAREHOUSE_SUMMARY_QUERY = """
SELECT 'dim_customers' AS table_name, count(*) AS row_count FROM public.dim_customers
UNION ALL SELECT 'dim_employees', count(*) FROM public.dim_employees
UNION ALL SELECT 'dim_products', count(*) FROM public.dim_products
UNION ALL SELECT 'dim_store_branch', count(*) FROM public.dim_store_branch
UNION ALL SELECT 'fct_order', count(*) FROM public.fct_order
UNION ALL SELECT 'fct_inventory', count(*) FROM public.fct_inventory
ORDER BY table_name
"""


@dataclass
class PipelineRunner(PipelineJob):
    """Main pipeline runner that executes staging then warehouse."""

    name: str
    staging_pipeline: StagingPipeline
    warehouse_pipeline: WarehousePipeline

    def run(self) -> None:
        logger.info("Starting pipeline %s", self.name)
        self.staging_pipeline.run()
        self.warehouse_pipeline.run()
        logger.info("Finished pipeline %s", self.name)


def build_pipeline(settings: PipelineSettings) -> PipelineRunner:
    project_root = Path(__file__).resolve().parents[3]
    batch_context = BatchContext.create()
    source_database = DatabaseClient("source_db", settings.source_db.url)
    staging_database = DatabaseClient("staging_db", settings.staging_db.url)
    warehouse_database = DatabaseClient("warehouse_db", settings.warehouse_db.url)
    log_database = DatabaseClient("log_db", settings.log_db.url)
    log_repository = PipelineLogRepository(log_database)
    failed_data_storage = MinioObjectStorageClient(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        bucket_name=settings.failed_data_bucket,
        compose_directory=project_root / "data_pipeline_paccafe",
    )

    staging_pipeline = StagingPipeline(
        name="staging",
        jobs=[
            SourceToStagingJob(
                name=f"load_{table}_to_staging",
                source_table=table,
                staging_table=table,
                source_database=source_database,
                staging_database=staging_database,
                batch_context=batch_context,
                log_repository=log_repository,
                failed_data_storage=failed_data_storage,
            )
            for table in SOURCE_TABLES
        ],
    )
    staging_pipeline.jobs.append(
        SpreadsheetCopyToStagingJob(
            name="load_store_branch_spreadsheet_to_staging",
            csv_path=project_root / settings.store_branch_csv_path,
            staging_table="store_branch",
            staging_database=staging_database,
            batch_context=batch_context,
            log_repository=log_repository,
            failed_data_storage=failed_data_storage,
        )
    )
    warehouse_pipeline = WarehousePipeline(
        name="warehouse",
        jobs=[
            WarehouseStagingSyncJob(
                name="sync_staging_tables_to_warehouse",
                tables=STAGING_TABLES,
                staging_database=staging_database,
                warehouse_database=warehouse_database,
                log_repository=log_repository,
                failed_data_storage=failed_data_storage,
                batch_context=batch_context,
            ),
            WarehouseSqlJob(
                name="load_warehouse_dimensions_and_facts",
                sql=LOAD_WAREHOUSE_SQL,
                warehouse_database=warehouse_database,
                log_repository=log_repository,
                failed_data_storage=failed_data_storage,
                batch_context=batch_context,
                summary_query=WAREHOUSE_SUMMARY_QUERY,
            ),
        ],
    )

    return PipelineRunner(
        name="data_pipeline_paccafe-source-staging-warehouse",
        staging_pipeline=staging_pipeline,
        warehouse_pipeline=warehouse_pipeline,
    )


def main() -> None:
    settings = PipelineSettings.from_env()
    configure_logging(settings.log_level)
    runner = build_pipeline(settings)
    runner.run()
