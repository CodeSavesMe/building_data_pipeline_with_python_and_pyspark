from __future__ import annotations

import logging

import pandas as pd

from pac_car.clients.database_client import PostgresClient


class CarSalesLoader:
    """Loads raw and transformed data into staging and warehouse databases."""

    STAGING_SALES_COLUMNS = [
        "id_sales",
        "year",
        "brand_car",
        "transmission",
        "state",
        "condition",
        "odometer",
        "color",
        "interior",
        "mmr",
        "sellingprice",
    ]
    STAGING_BRAND_COLUMNS = ["brand_car_id", "brand_name"]
    STAGING_STATE_COLUMNS = ["id_state", "code", "name"]
    WAREHOUSE_SALES_COLUMNS = [
        "id_sales_nk",
        "year",
        "brand_car_id",
        "transmission",
        "id_state",
        "condition",
        "odometer",
        "color",
        "interior",
        "mmr",
        "selling_price",
    ]

    def __init__(
        self,
        staging_db: PostgresClient,
        warehouse_db: PostgresClient,
        logger: logging.Logger,
    ) -> None:
        self._staging_db = staging_db
        self._warehouse_db = warehouse_db
        self._logger = logger

    def load_staging_sales(self, dataframe: pd.DataFrame) -> int:
        self._logger.info("Loading raw sales data to staging")
        return self._staging_db.replace_dataframe(
            dataframe[self.STAGING_SALES_COLUMNS].copy(),
            "car_sales",
        )

    def load_staging_brands(self, dataframe: pd.DataFrame) -> int:
        self._logger.info("Loading brand reference data to staging")
        return self._staging_db.replace_dataframe(
            dataframe[self.STAGING_BRAND_COLUMNS].copy(),
            "car_brand",
        )

    def load_staging_states(self, dataframe: pd.DataFrame) -> int:
        self._logger.info("Loading state reference data to staging")
        return self._staging_db.replace_dataframe(
            dataframe[self.STAGING_STATE_COLUMNS].copy(),
            "us_state",
        )

    def load_warehouse_sales(self, dataframe: pd.DataFrame) -> int:
        self._logger.info("Loading transformed sales data to warehouse")
        return self._warehouse_db.replace_dataframe(
            dataframe[self.WAREHOUSE_SALES_COLUMNS].copy(),
            "car_sales",
        )
