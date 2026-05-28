from paccafe_pipeline.config import PipelineSettings, PostgresSettings


def test_postgres_settings_builds_connection_url() -> None:
    settings = PostgresSettings(
        database="paccafe",
        host="localhost",
        user="postgres",
        password="postgres",
        port=5433,
    )

    assert settings.url == "postgresql://postgres:postgres@localhost:5433/paccafe"


def test_pipeline_settings_defaults_match_local_env(monkeypatch) -> None:
    for prefix in ("SRC", "STG", "WH", "LOG"):
        for key in ("POSTGRES_DB", "POSTGRES_HOST", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_PORT"):
            monkeypatch.delenv(f"{prefix}_{key}", raising=False)

    settings = PipelineSettings.from_env()

    assert settings.source_db.database == "paccafe"
    assert settings.source_db.port == 5433
    assert settings.staging_db.database == "staging"
    assert settings.staging_db.port == 5434
    assert settings.warehouse_db.database == "warehouse"
    assert settings.warehouse_db.port == 5435
    assert settings.log_db.database == "pipeline_log"
    assert settings.log_db.port == 5436
    assert str(settings.store_branch_csv_path) == "data/source/store_branch_paccofee.csv"
    assert settings.minio_endpoint == "localhost:9000"
    assert settings.minio_access_key == "minioadmin"
    assert settings.minio_secret_key == "minioadmin"
