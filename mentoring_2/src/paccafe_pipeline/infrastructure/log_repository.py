from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from paccafe_pipeline.infrastructure.database import DatabaseClient


@dataclass
class PipelineLogRepository:
    """Persist ETL job status into the pipeline log database."""

    database: DatabaseClient

    def log(
        self,
        step: str,
        component: str,
        status: str,
        table_name: str | None = None,
        error_msg: str | None = None,
    ) -> None:
        self.database.copy_rows(
            table_name="etl_log",
            rows=[
                {
                    "step": step,
                    "component": component,
                    "status": status,
                    "table_name": table_name,
                    "etl_date": datetime.now(timezone.utc).isoformat(),
                    "error_msg": error_msg,
                }
            ],
            columns=["step", "component", "status", "table_name", "etl_date", "error_msg"],
        )
