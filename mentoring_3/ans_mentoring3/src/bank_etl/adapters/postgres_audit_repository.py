import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import psycopg2
from loguru import logger
from psycopg2.extras import Json

from bank_etl.domain.models import ChangeSummary, DataProfile
from bank_etl.infrastructure.config import DatabaseSettings
from bank_etl.infrastructure.retry import RetryPolicy
from bank_etl.ports.audit import RunAuditRepository


@dataclass
class PostgresRunAuditRepository(RunAuditRepository):
    database: DatabaseSettings
    retry_policy: RetryPolicy

    def start_run(self) -> str:
        run_id = str(uuid4())

        def operation() -> None:
            self._ensure_schema()
            with psycopg2.connect(**self.database.psycopg_options) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO etl_pipeline_runs (run_id, status) VALUES (%s, 'RUNNING')",
                        (run_id,),
                    )

        self.retry_policy.execute(operation, "start ETL audit run")
        logger.info("ETL audit run created: {}", run_id)
        return run_id

    def save_profiles(self, run_id: str, profiles: tuple[DataProfile, ...]) -> None:
        def operation() -> None:
            with psycopg2.connect(**self.database.psycopg_options) as connection:
                with connection.cursor() as cursor:
                    for profile in profiles:
                        cursor.execute(
                            """
                            INSERT INTO etl_data_profiles (
                                run_id, stage, dataset_name, row_count, column_count,
                                null_count, duplicate_key_count, null_by_column,
                                previous_row_count, row_count_delta
                            )
                            SELECT
                                %s, %s, %s, %s, %s, %s, %s, %s,
                                previous.row_count,
                                CASE WHEN previous.row_count IS NULL THEN NULL
                                     ELSE %s - previous.row_count END
                            FROM (SELECT 1) AS seed
                            LEFT JOIN LATERAL (
                                SELECT profile.row_count
                                FROM etl_data_profiles AS profile
                                JOIN etl_pipeline_runs AS run
                                  ON run.run_id = profile.run_id
                                WHERE profile.stage = %s
                                  AND profile.dataset_name = %s
                                  AND run.status = 'SUCCEEDED'
                                ORDER BY run.finished_at DESC
                                LIMIT 1
                            ) AS previous ON TRUE
                            """,
                            (
                                run_id,
                                profile.stage.value,
                                profile.dataset_name,
                                profile.row_count,
                                profile.column_count,
                                profile.null_count,
                                profile.duplicate_key_count,
                                Json(profile.null_by_column),
                                profile.row_count,
                                profile.stage.value,
                                profile.dataset_name,
                            ),
                        )

        self.retry_policy.execute(operation, "persist data profiles")

    def save_changes(self, run_id: str, changes: tuple[ChangeSummary, ...]) -> None:
        def operation() -> None:
            with psycopg2.connect(**self.database.psycopg_options) as connection:
                with connection.cursor() as cursor:
                    cursor.executemany(
                        """
                        INSERT INTO etl_change_summary (
                            run_id, dataset_name, inserted_count, updated_count,
                            deleted_count, unchanged_count
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        [
                            (
                                run_id,
                                change.table.value,
                                change.inserted_count,
                                change.updated_count,
                                change.deleted_count,
                                change.unchanged_count,
                            )
                            for change in changes
                        ],
                    )

        self.retry_policy.execute(operation, "persist semi-CDC summary")

    def mark_succeeded(self, run_id: str, duration_seconds: float) -> None:
        self._update_status(run_id, "SUCCEEDED", duration_seconds, None)

    def mark_failed(self, run_id: str, error_message: str) -> None:
        self._update_status(run_id, "FAILED", None, error_message[:4000])

    def export_summary(self, run_id: str, path: Path) -> None:
        def operation() -> dict[str, object]:
            with psycopg2.connect(**self.database.psycopg_options) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT status, started_at, finished_at, duration_seconds,
                               error_message
                        FROM etl_pipeline_runs WHERE run_id = %s
                        """,
                        (run_id,),
                    )
                    run = cursor.fetchone()
                    cursor.execute(
                        """
                        SELECT stage, dataset_name, row_count, column_count,
                               null_count, duplicate_key_count, null_by_column,
                               previous_row_count, row_count_delta
                        FROM etl_data_profiles
                        WHERE run_id = %s ORDER BY stage, dataset_name
                        """,
                        (run_id,),
                    )
                    profiles = cursor.fetchall()
                    cursor.execute(
                        """
                        SELECT dataset_name, inserted_count, updated_count,
                               deleted_count, unchanged_count
                        FROM etl_change_summary
                        WHERE run_id = %s ORDER BY dataset_name
                        """,
                        (run_id,),
                    )
                    changes = cursor.fetchall()
            return self._summary_payload(run_id, run, profiles, changes)

        payload = self.retry_policy.execute(operation, "export ETL profile summary")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, default=self._json_default) + "\n")
        logger.info("Latest ETL profile summary exported to {}", path)

    def _update_status(
        self,
        run_id: str,
        status: str,
        duration_seconds: float | None,
        error_message: str | None,
    ) -> None:
        def operation() -> None:
            with psycopg2.connect(**self.database.psycopg_options) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE etl_pipeline_runs
                        SET status = %s, finished_at = CURRENT_TIMESTAMP,
                            duration_seconds = %s, error_message = %s
                        WHERE run_id = %s
                        """,
                        (status, duration_seconds, error_message, run_id),
                    )

        self.retry_policy.execute(operation, f"mark ETL run {status.lower()}")

    def _ensure_schema(self) -> None:
        with psycopg2.connect(**self.database.psycopg_options) as connection:
            with connection.cursor() as cursor:
                cursor.execute(AUDIT_SCHEMA_SQL)

    @staticmethod
    def _summary_payload(
        run_id: str,
        run: tuple | None,
        profiles: list[tuple],
        changes: list[tuple],
    ) -> dict[str, object]:
        if run is None:
            raise RuntimeError(f"Audit run not found: {run_id}")
        return {
            "run_id": run_id,
            "status": run[0],
            "started_at": run[1],
            "finished_at": run[2],
            "duration_seconds": run[3],
            "error_message": run[4],
            "profiles": [
                {
                    "stage": row[0],
                    "dataset": row[1],
                    "row_count": row[2],
                    "column_count": row[3],
                    "null_count": row[4],
                    "duplicate_key_count": row[5],
                    "null_by_column": row[6],
                    "previous_row_count": row[7],
                    "row_count_delta": row[8],
                }
                for row in profiles
            ],
            "changes": [
                {
                    "dataset": row[0],
                    "inserted": row[1],
                    "updated": row[2],
                    "deleted": row[3],
                    "unchanged": row[4],
                }
                for row in changes
            ],
        }

    @staticmethod
    def _json_default(value: object) -> str:
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)


AUDIT_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS etl_pipeline_runs (
    run_id UUID PRIMARY KEY,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    duration_seconds NUMERIC(12, 2),
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS etl_data_profiles (
    profile_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_pipeline_runs(run_id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL,
    dataset_name VARCHAR(255) NOT NULL,
    row_count BIGINT NOT NULL,
    column_count INT NOT NULL,
    null_count BIGINT NOT NULL,
    duplicate_key_count BIGINT NOT NULL,
    null_by_column JSONB NOT NULL,
    previous_row_count BIGINT,
    row_count_delta BIGINT,
    profiled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (run_id, stage, dataset_name)
);

CREATE TABLE IF NOT EXISTS etl_change_summary (
    change_id BIGSERIAL PRIMARY KEY,
    run_id UUID NOT NULL REFERENCES etl_pipeline_runs(run_id) ON DELETE CASCADE,
    dataset_name VARCHAR(255) NOT NULL,
    inserted_count BIGINT NOT NULL,
    updated_count BIGINT NOT NULL,
    deleted_count BIGINT NOT NULL,
    unchanged_count BIGINT NOT NULL,
    detected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (run_id, dataset_name)
);
"""
