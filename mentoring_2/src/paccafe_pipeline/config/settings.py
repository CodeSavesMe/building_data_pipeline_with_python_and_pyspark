from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PostgresSettings:
    """Connection settings for one PostgreSQL service."""

    database: str
    host: str
    user: str
    password: str
    port: int

    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    @classmethod
    def from_env(cls, prefix: str, default_database: str, default_port: int) -> "PostgresSettings":
        return cls(
            database=os.getenv(f"{prefix}_POSTGRES_DB", default_database),
            host=os.getenv(f"{prefix}_POSTGRES_HOST", "localhost"),
            user=os.getenv(f"{prefix}_POSTGRES_USER", "postgres"),
            password=os.getenv(f"{prefix}_POSTGRES_PASSWORD", "postgres"),
            port=int(os.getenv(f"{prefix}_POSTGRES_PORT", str(default_port))),
        )


@dataclass(frozen=True)
class PipelineSettings:
    """Runtime settings loaded from environment variables."""

    environment: str
    log_level: str
    source_db: PostgresSettings
    staging_db: PostgresSettings
    warehouse_db: PostgresSettings
    log_db: PostgresSettings
    store_branch_csv_path: Path
    minio_endpoint: str | None
    minio_access_key: str | None
    minio_secret_key: str | None
    failed_data_bucket: str

    @classmethod
    def from_env(cls) -> "PipelineSettings":
        return cls(
            environment=os.getenv("APP_ENV", "local"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            source_db=PostgresSettings.from_env("SRC", "paccafe", 5433),
            staging_db=PostgresSettings.from_env("STG", "staging", 5434),
            warehouse_db=PostgresSettings.from_env("WH", "warehouse", 5435),
            log_db=PostgresSettings.from_env("LOG", "pipeline_log", 5436),
            store_branch_csv_path=Path(os.getenv("STORE_BRANCH_CSV_PATH", "data/source/store_branch_paccofee.csv")),
            minio_endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
            minio_access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            minio_secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            failed_data_bucket=os.getenv("FAILED_DATA_BUCKET", "failed-data"),
        )
