from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency exists in normal runtime
    load_dotenv = None


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPOSITORY_ROOT = PROJECT_ROOT.parent
DEFAULT_DATASET_ROOT = REPOSITORY_ROOT / "dataset"


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database: str
    username: str
    password: str

    @property
    def sqlalchemy_url(self) -> str:
        return (
            "postgresql+psycopg2://"
            f"{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        )


@dataclass(frozen=True)
class MinioSettings:
    endpoint_url: str
    access_key: str
    secret_key: str
    bucket_name: str


@dataclass(frozen=True)
class PipelineSettings:
    source_db: DatabaseSettings
    staging_db: DatabaseSettings
    warehouse_db: DatabaseSettings
    log_db: DatabaseSettings
    minio: MinioSettings
    brand_reference_path: Path
    state_reference_path: Path
    artifact_dir: Path
    log_dir: Path
    model_test_size: float
    model_random_seed: int
    mlflow_tracking_uri: str | None
    spark_master_url: str | None


def load_settings() -> PipelineSettings:
    dataset_root = _resolve_path(os.getenv("DATASET_ROOT"), DEFAULT_DATASET_ROOT)
    dataset_env_path = dataset_root / "data_pipeline_exercise_4" / ".env"

    if load_dotenv is not None:
        load_dotenv(dataset_env_path)
        load_dotenv(PROJECT_ROOT / ".env", override=True)

    dataset_root = _resolve_path(os.getenv("DATASET_ROOT"), DEFAULT_DATASET_ROOT)
    return PipelineSettings(
        source_db=_load_database_settings("SRC", default_port=15435, default_database="source_db"),
        staging_db=_load_database_settings(
            "STG", default_port=15436, default_database="staging_db"
        ),
        warehouse_db=_load_database_settings(
            "WH", default_port=15437, default_database="warehouse_db"
        ),
        log_db=_load_database_settings("LOG", default_port=15438, default_database="log_db"),
        minio=MinioSettings(
            endpoint_url=_get_env("MINIO_ENDPOINT_URL", "http://localhost:19004"),
            access_key=_get_env("MINIO_ACCESS_KEY", "admin"),
            secret_key=_get_env("MINIO_SECRET_KEY", "admin1234"),
            bucket_name=_get_env("MINIO_BUCKET_NAME", "pac-car-models"),
        ),
        brand_reference_path=_resolve_path(
            os.getenv("BRAND_REFERENCE_PATH"),
            dataset_root / "car_brand.csv",
        ),
        state_reference_path=_resolve_path(
            os.getenv("STATE_REFERENCE_PATH"),
            dataset_root / "api_data.json",
        ),
        artifact_dir=_resolve_path(
            os.getenv("ARTIFACT_DIR"), PROJECT_ROOT / "artifacts" / "models"
        ),
        log_dir=_resolve_path(os.getenv("LOG_DIR"), PROJECT_ROOT / "logs"),
        model_test_size=float(_get_env("MODEL_TEST_SIZE", "0.2")),
        model_random_seed=int(_get_env("MODEL_RANDOM_SEED", "42")),
        mlflow_tracking_uri=os.getenv("MLFLOW_TRACKING_URI") or None,
        spark_master_url=os.getenv("SPARK_MASTER_URL") or None,
    )


def _load_database_settings(
    prefix: str,
    *,
    default_port: int,
    default_database: str,
) -> DatabaseSettings:
    return DatabaseSettings(
        host=_get_env(f"{prefix}_POSTGRES_HOST", "localhost"),
        port=int(_get_env(f"{prefix}_POSTGRES_PORT", str(default_port))),
        database=_get_env(f"{prefix}_POSTGRES_DB", default_database),
        username=_get_env(f"{prefix}_POSTGRES_USER", "admin"),
        password=_get_env(f"{prefix}_POSTGRES_PASSWORD", "admin"),
    )


def _get_env(key: str, default: str) -> str:
    value = os.getenv(key)
    return value if value not in (None, "") else default


def _resolve_path(value: str | None, default: Path) -> Path:
    if value in (None, ""):
        return default.resolve()

    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()
