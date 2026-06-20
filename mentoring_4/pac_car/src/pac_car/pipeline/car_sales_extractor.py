from __future__ import annotations

import logging

import pandas as pd

from pac_car.clients.database_client import PostgresClient
from pac_car.clients.reference_api_client import StateReferenceClient
from pac_car.clients.spreadsheet_client import BrandReferenceClient


class CarSalesExtractor:
    """Extracts car sales and reference data from source systems."""

    def __init__(
        self,
        source_db: PostgresClient,
        staging_db: PostgresClient,
        warehouse_db: PostgresClient,
        brand_reference_client: BrandReferenceClient,
        state_reference_client: StateReferenceClient,
        logger: logging.Logger,
    ) -> None:
        self._source_db = source_db
        self._staging_db = staging_db
        self._warehouse_db = warehouse_db
        self._brand_reference_client = brand_reference_client
        self._state_reference_client = state_reference_client
        self._logger = logger

    def extract_source_sales(self) -> pd.DataFrame:
        self._logger.info("Extracting sales data from source database")
        return self._source_db.fetch_dataframe(
            """
            SELECT
                id_sales,
                "year"::text AS "year",
                brand_car,
                transmission,
                state,
                "condition"::text AS "condition",
                odometer::text AS odometer,
                color,
                interior,
                mmr::text AS mmr,
                sellingprice::text AS sellingprice
            FROM public.car_sales
            ORDER BY id_sales
            """
        )

    def extract_brand_reference(self) -> pd.DataFrame:
        return self._brand_reference_client.read_brands()

    def extract_state_reference(self) -> pd.DataFrame:
        return self._state_reference_client.read_states()

    def extract_staging_sales(self) -> pd.DataFrame:
        self._logger.info("Extracting sales data from staging database")
        return self._staging_db.fetch_dataframe(
            """
            SELECT
                id_sales,
                "year",
                brand_car,
                transmission,
                state,
                "condition",
                odometer,
                color,
                interior,
                mmr,
                sellingprice
            FROM public.car_sales
            ORDER BY id_sales
            """
        )

    def extract_staging_brands(self) -> pd.DataFrame:
        self._logger.info("Extracting brand reference from staging database")
        return self._staging_db.fetch_dataframe(
            """
            SELECT brand_car_id, brand_name
            FROM public.car_brand
            ORDER BY brand_car_id
            """
        )

    def extract_staging_states(self) -> pd.DataFrame:
        self._logger.info("Extracting state reference from staging database")
        return self._staging_db.fetch_dataframe(
            """
            SELECT id_state, code, "name"
            FROM public.us_state
            ORDER BY id_state
            """
        )

    def extract_warehouse_sales(self) -> pd.DataFrame:
        self._logger.info("Extracting model-ready sales data from warehouse database")
        return self._warehouse_db.fetch_dataframe(
            """
            SELECT
                sales_id,
                id_sales_nk,
                "year",
                brand_car_id,
                transmission,
                id_state,
                "condition",
                odometer,
                color,
                interior,
                mmr,
                selling_price
            FROM public.car_sales
            ORDER BY id_sales_nk
            """
        )
