from __future__ import annotations

import json
import logging
from pathlib import Path
from time import sleep

import pandas as pd
import requests


class StateReferenceClient:
    """Reads state reference data from a REST API or the local API fixture."""

    REQUIRED_COLUMNS = ["id_state", "code", "name"]

    def __init__(
        self,
        local_file_path: Path,
        logger: logging.Logger,
        *,
        api_url: str | None = None,
        max_retries: int = 3,
        retry_delay_seconds: float = 1.0,
    ) -> None:
        self._local_file_path = local_file_path
        self._api_url = api_url
        self._max_retries = max_retries
        self._retry_delay_seconds = retry_delay_seconds
        self._logger = logger

    def read_states(self) -> pd.DataFrame:
        payload = self._read_remote_payload() if self._api_url else self._read_local_payload()
        records = (
            payload["regions"] if isinstance(payload, dict) and "regions" in payload else payload
        )
        dataframe = pd.DataFrame.from_records(records)
        missing_columns = set(self.REQUIRED_COLUMNS) - set(dataframe.columns)
        if missing_columns:
            raise ValueError(f"State reference is missing columns: {sorted(missing_columns)}")

        return dataframe[self.REQUIRED_COLUMNS].copy()

    def _read_remote_payload(self) -> object:
        if self._api_url is None:
            raise ValueError("API URL is not configured")

        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                self._logger.info("Fetching state reference from API, attempt %s", attempt)
                response = requests.get(self._api_url, timeout=15)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_error = exc
                self._logger.warning("State API request failed: %s", exc)
                sleep(self._retry_delay_seconds)

        raise RuntimeError("State API request failed after all retries") from last_error

    def _read_local_payload(self) -> object:
        self._logger.info("Reading state reference from %s", self._local_file_path)
        with self._local_file_path.open("r", encoding="utf-8") as file:
            return json.load(file)
