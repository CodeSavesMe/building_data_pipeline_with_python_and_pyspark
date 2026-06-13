import signal
from types import FrameType

from loguru import logger
from pyspark.sql import SparkSession

from bank_etl.adapters.csv_reader import SparkCsvReader
from bank_etl.adapters.postgres_audit_repository import PostgresRunAuditRepository
from bank_etl.adapters.postgres_reader import PostgresJdbcReader
from bank_etl.adapters.postgres_writer import PostgresWarehouseWriter
from bank_etl.adapters.spark_change_detector import SparkBatchChangeDetector
from bank_etl.adapters.spark_profiler import SparkDataProfiler
from bank_etl.adapters.spark_transformer import SparkDataTransformer
from bank_etl.application.etl_service import ETLService
from bank_etl.infrastructure.config import Settings
from bank_etl.infrastructure.logger import configure_logger, shutdown_logger
from bank_etl.infrastructure.retry import RetryPolicy
from bank_etl.infrastructure.spark import SparkSessionFactory


def _request_shutdown(signum: int, _frame: FrameType | None) -> None:
    logger.warning("Received signal {}; shutting down cleanly", signum)
    raise SystemExit(128 + signum)


def main() -> None:
    settings = Settings.from_env()
    configure_logger(settings.log_path)
    signal.signal(signal.SIGTERM, _request_shutdown)
    signal.signal(signal.SIGINT, _request_shutdown)
    spark: SparkSession | None = None

    try:
        spark = SparkSessionFactory(settings.spark).create()
        retry_policy = RetryPolicy(settings.retry)
        service = ETLService(
            database_reader=PostgresJdbcReader(
                spark,
                settings.source_db,
                retry_policy,
            ),
            file_reader=SparkCsvReader(spark, retry_policy),
            transformer=SparkDataTransformer(settings.max_valid_year),
            profiler=SparkDataProfiler(),
            change_detector=SparkBatchChangeDetector(
                spark,
                settings.warehouse_db,
                retry_policy,
            ),
            warehouse_writer=PostgresWarehouseWriter(
                settings.warehouse_db,
                retry_policy,
            ),
            audit_repository=PostgresRunAuditRepository(
                settings.warehouse_db,
                retry_policy,
            ),
            csv_path=settings.csv_path,
            profile_report_path=settings.profile_report_path,
        )
        service.run()
    except Exception:
        logger.exception("ETL pipeline terminated with an error")
        raise
    finally:
        if spark is not None:
            logger.info("Stopping Spark session")
            spark.stop()
        shutdown_logger()


if __name__ == "__main__":
    main()
