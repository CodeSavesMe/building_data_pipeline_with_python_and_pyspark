import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _read_env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else default


def _positive_int(name: str, default: str) -> int:
    value = int(_read_env(name, default))
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


def _positive_float(name: str, default: str) -> float:
    value = float(_read_env(name, default))
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return value


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    user: str
    password: str
    connect_timeout_seconds: int
    socket_timeout_seconds: int

    @property
    def jdbc_url(self) -> str:
        return f"jdbc:postgresql://{self.host}:{self.port}/{self.database}"

    @property
    def jdbc_options(self) -> dict[str, str]:
        return {
            "url": self.jdbc_url,
            "user": self.user,
            "password": self.password,
            "driver": "org.postgresql.Driver",
            "connectTimeout": str(self.connect_timeout_seconds),
            "socketTimeout": str(self.socket_timeout_seconds),
            "tcpKeepAlive": "true",
        }

    @property
    def psycopg_options(self) -> dict[str, str | int]:
        return {
            "host": self.host,
            "port": self.port,
            "dbname": self.database,
            "user": self.user,
            "password": self.password,
            "connect_timeout": self.connect_timeout_seconds,
            "options": f"-c statement_timeout={self.socket_timeout_seconds * 1000}",
        }


@dataclass(frozen=True)
class RetrySettings:
    attempts: int
    initial_delay_seconds: float
    maximum_delay_seconds: float


@dataclass(frozen=True)
class SparkSettings:
    app_name: str
    master: str
    driver_memory: str
    shuffle_partitions: int
    jdbc_driver_path: Path


@dataclass(frozen=True)
class Settings:
    source_db: DatabaseSettings
    warehouse_db: DatabaseSettings
    retry: RetrySettings
    spark: SparkSettings
    csv_path: Path
    log_path: Path
    profile_report_path: Path
    max_valid_year: int

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        connect_timeout = _positive_int("DB_CONNECT_TIMEOUT_SECONDS", "10")
        socket_timeout = _positive_int("DB_SOCKET_TIMEOUT_SECONDS", "60")

        return cls(
            source_db=DatabaseSettings(
                host=_read_env("SOURCE_DB_HOST", "source_db"),
                port=_positive_int("SOURCE_DB_PORT", "5432"),
                database=_read_env("SOURCE_DB_NAME", "source"),
                user=_read_env("SOURCE_DB_USER", "postgres"),
                password=_read_env("SOURCE_DB_PASSWORD", "postgres"),
                connect_timeout_seconds=connect_timeout,
                socket_timeout_seconds=socket_timeout,
            ),
            warehouse_db=DatabaseSettings(
                host=_read_env("WAREHOUSE_DB_HOST", "data_warehouse"),
                port=_positive_int("WAREHOUSE_DB_PORT", "5432"),
                database=_read_env("WAREHOUSE_DB_NAME", "data_warehouse"),
                user=_read_env("WAREHOUSE_DB_USER", "postgres"),
                password=_read_env("WAREHOUSE_DB_PASSWORD", "postgres"),
                connect_timeout_seconds=connect_timeout,
                socket_timeout_seconds=socket_timeout,
            ),
            retry=RetrySettings(
                attempts=_positive_int("RETRY_ATTEMPTS", "3"),
                initial_delay_seconds=_positive_float("RETRY_INITIAL_DELAY_SECONDS", "2"),
                maximum_delay_seconds=_positive_float("RETRY_MAX_DELAY_SECONDS", "15"),
            ),
            spark=SparkSettings(
                app_name=_read_env("SPARK_APP_NAME", "bank-etl-pipeline"),
                master=_read_env("SPARK_MASTER", "local[4]"),
                driver_memory=_read_env("SPARK_DRIVER_MEMORY", "1g"),
                shuffle_partitions=_positive_int("SPARK_SHUFFLE_PARTITIONS", "8"),
                jdbc_driver_path=Path(
                    _read_env(
                        "JDBC_DRIVER_PATH",
                        "/opt/spark/jars/postgresql-42.6.0.jar",
                    )
                ),
            ),
            csv_path=Path(_read_env("CSV_PATH", "/app/data/new_bank_transactions.csv")),
            log_path=Path(_read_env("LOG_PATH", "/app/logs/etl_pipeline.log")),
            profile_report_path=Path(
                _read_env(
                    "PROFILE_REPORT_PATH",
                    "/app/logs/latest_profile_summary.json",
                )
            ),
            max_valid_year=_positive_int("MAX_VALID_YEAR", "2025"),
        )
