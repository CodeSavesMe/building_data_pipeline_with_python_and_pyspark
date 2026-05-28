from __future__ import annotations

import csv
import io
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable

from paccafe_pipeline.infrastructure.sql_reader import read_sql_file


class DatabaseClient:
    """PostgreSQL adapter implemented through the local psql client."""

    def __init__(self, name: str, connection_url: str) -> None:
        self.name = name
        self.connection_url = connection_url

    def execute(self, sql: str, parameters: dict[str, Any] | None = None) -> None:
        """Execute a SQL statement."""
        if parameters:
            raise NotImplementedError("Parameterized SQL is not supported by this psql adapter.")

        self._run_psql(["-c", sql])

    def execute_sql_file(self, sql_path: Path) -> None:
        sql = read_sql_file(sql_path)
        self.execute(sql)

    def fetch_dicts(self, query: str) -> list[dict[str, str]]:
        """Run a query and return CSV rows as dictionaries."""

        result = self._run_psql(
            ["-c", f"COPY ({query}) TO STDOUT WITH CSV HEADER"],
            capture_output=True,
        )
        return list(csv.DictReader(io.StringIO(result.stdout)))

    def read_table(self, table_name: str, schema: str = "public") -> list[dict[str, str]]:
        """Read a table as dictionaries."""

        return self.fetch_dicts(f"SELECT * FROM {qualified_name(schema, table_name)}")

    def write_table(self, data: Any, table_name: str, schema: str = "public") -> None:
        """Write data to a database table."""
        if not isinstance(data, list):
            raise TypeError("write_table expects a list of dictionaries.")
        self.copy_rows(table_name=table_name, rows=data, schema=schema)

    def table_count(self, table_name: str, schema: str = "public") -> int:
        rows = self.fetch_dicts(f"SELECT count(*) AS row_count FROM {qualified_name(schema, table_name)}")
        return int(rows[0]["row_count"])

    def truncate_table(self, table_name: str, schema: str = "public", cascade: bool = False) -> None:
        cascade_sql = " CASCADE" if cascade else ""
        self.execute(f"TRUNCATE TABLE {qualified_name(schema, table_name)}{cascade_sql}")

    def list_columns(self, table_name: str, schema: str = "public") -> list[str]:
        rows = self.fetch_dicts(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = '%s'
              AND table_name = '%s'
            ORDER BY ordinal_position
            """
            % (escape_literal(schema), escape_literal(table_name))
        )
        return [row["column_name"] for row in rows]

    def describe_columns(self, table_name: str, schema: str = "public") -> list[dict[str, str]]:
        return self.fetch_dicts(
            """
            SELECT
                column_name,
                data_type,
                udt_name,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = '%s'
              AND table_name = '%s'
            ORDER BY ordinal_position
            """
            % (escape_literal(schema), escape_literal(table_name))
        )

    def create_schema(self, schema: str) -> None:
        self.execute(f"CREATE SCHEMA IF NOT EXISTS {quote_identifier(schema)}")

    def drop_table_if_exists(self, table_name: str, schema: str = "public") -> None:
        self.execute(f"DROP TABLE IF EXISTS {qualified_name(schema, table_name)}")

    def create_table_from_columns(
        self,
        table_name: str,
        columns: list[dict[str, str]],
        schema: str = "public",
    ) -> None:
        column_sql = ", ".join(
            f"{quote_identifier(column['column_name'])} {postgres_type_sql(column)}"
            for column in columns
        )
        self.execute(f"CREATE TABLE {qualified_name(schema, table_name)} ({column_sql})")

    def copy_rows(
        self,
        table_name: str,
        rows: list[dict[str, Any]],
        schema: str = "public",
        columns: list[str] | None = None,
    ) -> int:
        if not rows:
            return 0

        selected_columns = columns or list(rows[0].keys())
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=selected_columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

        return self.copy_csv(
            table_name=table_name,
            csv_payload=buffer.getvalue(),
            columns=selected_columns,
            schema=schema,
        )

    def copy_csv(
        self,
        table_name: str,
        csv_payload: str,
        columns: Iterable[str],
        schema: str = "public",
    ) -> int:
        column_sql = ", ".join(quote_identifier(column) for column in columns)
        sql = f"COPY {qualified_name(schema, table_name)} ({column_sql}) FROM STDIN WITH CSV HEADER"
        self._run_psql(["-c", sql], input_text=csv_payload)
        return max(len(csv_payload.splitlines()) - 1, 0)

    def copy_query_to_table(
        self,
        query: str,
        target: "DatabaseClient",
        target_table: str,
        target_columns: list[str],
        target_schema: str = "public",
    ) -> int:
        source_sql = f"COPY ({query}) TO STDOUT WITH CSV HEADER"
        source_result = self._run_psql(["-c", source_sql], capture_output=True)
        return target.copy_csv(
            table_name=target_table,
            csv_payload=source_result.stdout,
            columns=target_columns,
            schema=target_schema,
        )

    def _run_psql(
        self,
        args: list[str],
        input_text: str | None = None,
        capture_output: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        command = [
            "psql",
            self.connection_url,
            "-v",
            "ON_ERROR_STOP=1",
            "-X",
            "-q",
            *args,
        ]
        result = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"psql command failed for {self.name}: {message}")
        if capture_output:
            return result
        return result


def quote_identifier(identifier: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", identifier):
        raise ValueError(f"Unsafe SQL identifier: {identifier!r}")
    return f'"{identifier}"'


def qualified_name(schema: str, table_name: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(table_name)}"


def escape_literal(value: str) -> str:
    return value.replace("'", "''")


def postgres_type_sql(column: dict[str, str]) -> str:
    data_type = column["data_type"]
    max_length = column.get("character_maximum_length")
    precision = column.get("numeric_precision")
    scale = column.get("numeric_scale")

    if data_type == "character varying" and max_length:
        return f"varchar({int(max_length)})"
    if data_type == "numeric" and precision:
        if scale:
            return f"numeric({int(precision)}, {int(scale)})"
        return f"numeric({int(precision)})"
    if data_type == "integer":
        return "int4"
    if data_type == "boolean":
        return "bool"
    if data_type == "timestamp without time zone":
        return "timestamp"
    if data_type == "date":
        return "date"
    if data_type == "uuid":
        return "uuid"
    return data_type
