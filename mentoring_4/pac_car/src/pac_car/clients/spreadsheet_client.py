from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd


class BrandReferenceClient:
    """Reads brand reference data from the exported spreadsheet file."""

    REQUIRED_COLUMNS = ["brand_car_id", "brand_name"]

    def __init__(self, file_path: Path, logger: logging.Logger) -> None:
        self._file_path = file_path
        self._logger = logger

    def read_brands(self) -> pd.DataFrame:
        self._logger.info("Reading brand reference from %s", self._file_path)
        dataframe = pd.read_csv(self._file_path, sep="\t")
        missing_columns = set(self.REQUIRED_COLUMNS) - set(dataframe.columns)
        if missing_columns:
            raise ValueError(f"Brand reference is missing columns: {sorted(missing_columns)}")

        return dataframe[self.REQUIRED_COLUMNS].copy()
