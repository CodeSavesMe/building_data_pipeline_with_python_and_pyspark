import os
import sys
from pathlib import Path

from loguru import logger
from pyspark.sql import SparkSession

from bank_etl.infrastructure.config import SparkSettings


class SparkSessionFactory:
    def __init__(self, settings: SparkSettings) -> None:
        self._settings = settings

    def create(self) -> SparkSession:
        self._validate_driver(self._settings.jdbc_driver_path)
        os.environ["PYSPARK_PYTHON"] = sys.executable
        os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
        logger.info(
            "Creating Spark session app_name={} master={} driver_memory={}",
            self._settings.app_name,
            self._settings.master,
            self._settings.driver_memory,
        )
        spark = (
            SparkSession.builder.appName(self._settings.app_name)
            .master(self._settings.master)
            .config("spark.jars", str(self._settings.jdbc_driver_path))
            .config("spark.driver.memory", self._settings.driver_memory)
            .config(
                "spark.sql.shuffle.partitions",
                str(self._settings.shuffle_partitions),
            )
            .config("spark.sql.session.timeZone", "UTC")
            .config("spark.ui.port", "4040")
            .getOrCreate()
        )
        spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
        spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark {} initialized", spark.version)
        return spark

    @staticmethod
    def _validate_driver(driver_path: Path) -> None:
        if not driver_path.is_file():
            raise FileNotFoundError(f"PostgreSQL JDBC driver not found: {driver_path}")
