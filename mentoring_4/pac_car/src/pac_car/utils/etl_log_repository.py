from __future__ import annotations

import logging
from datetime import datetime

from pac_car.clients.database_client import PostgresClient


class EtlLogRepository:
    """Writes auditable pipeline step logs to the log database."""

    def __init__(self, database_client: PostgresClient, logger: logging.Logger) -> None:
        self._database_client = database_client
        self._logger = logger

    def write(
        self,
        *,
        step: str,
        component: str,
        status: str,
        table_name: str | None = None,
        error_message: str | None = None,
    ) -> None:
        try:
            self._database_client.execute(
                """
                INSERT INTO public.etl_log
                    (step, component, status, table_name, etl_date, error_msg)
                VALUES
                    (:step, :component, :status, :table_name, :etl_date, :error_msg)
                """,
                {
                    "step": step,
                    "component": component,
                    "status": status,
                    "table_name": table_name,
                    "etl_date": datetime.now(),
                    "error_msg": error_message,
                },
            )
        except Exception as exc:  # pragma: no cover - log DB failures should not hide root cause
            self._logger.warning("Failed to write ETL log to database: %s", exc)
