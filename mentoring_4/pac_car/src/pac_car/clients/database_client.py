from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from pac_car.config.settings import DatabaseSettings


class PostgresClient:
    """Small PostgreSQL client focused on dataframe IO and simple SQL execution."""

    def __init__(self, settings: DatabaseSettings, logger: logging.Logger) -> None:
        self._settings = settings
        self._logger = logger
        self._engine: Engine = create_engine(settings.sqlalchemy_url, pool_pre_ping=True)

    @property
    def engine(self) -> Engine:
        return self._engine

    def fetch_dataframe(
        self,
        query: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> pd.DataFrame:
        self._logger.debug("Fetching dataframe from %s", self._settings.database)
        with self._engine.connect() as connection:
            return pd.read_sql_query(text(query), connection, params=parameters)

    def execute(
        self,
        statement: str,
        parameters: Mapping[str, Any] | None = None,
    ) -> None:
        with self._engine.begin() as connection:
            connection.execute(text(statement), parameters or {})

    def truncate_table(self, table_name: str, *, schema: str = "public") -> None:
        quoted_schema = _quote_identifier(schema)
        quoted_table = _quote_identifier(table_name)
        self.execute(f"TRUNCATE TABLE {quoted_schema}.{quoted_table} RESTART IDENTITY CASCADE")

    def replace_dataframe(
        self,
        dataframe: pd.DataFrame,
        table_name: str,
        *,
        schema: str = "public",
    ) -> int:
        self.truncate_table(table_name, schema=schema)
        return self.append_dataframe(dataframe, table_name, schema=schema)

    def append_dataframe(
        self,
        dataframe: pd.DataFrame,
        table_name: str,
        *,
        schema: str = "public",
    ) -> int:
        if dataframe.empty:
            self._logger.warning("Skip writing empty dataframe to %s.%s", schema, table_name)
            return 0

        dataframe.to_sql(
            name=table_name,
            con=self._engine,
            schema=schema,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=1_000,
        )
        return len(dataframe)

    def count_rows(self, table_name: str, *, schema: str = "public") -> int:
        quoted_schema = _quote_identifier(schema)
        quoted_table = _quote_identifier(table_name)
        result = self.fetch_dataframe(
            f"SELECT COUNT(*) AS row_count FROM {quoted_schema}.{quoted_table}"
        )
        return int(result.loc[0, "row_count"])

    def dispose(self) -> None:
        self._engine.dispose()


def _quote_identifier(identifier: str) -> str:
    escaped = identifier.replace('"', '""')
    return f'"{escaped}"'
