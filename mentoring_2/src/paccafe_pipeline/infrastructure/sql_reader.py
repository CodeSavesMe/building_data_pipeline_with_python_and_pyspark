from __future__ import annotations

from pathlib import Path


def read_sql_file(path: Path) -> str:
    """Read a SQL file with a consistent encoding."""

    return path.read_text(encoding="utf-8")
