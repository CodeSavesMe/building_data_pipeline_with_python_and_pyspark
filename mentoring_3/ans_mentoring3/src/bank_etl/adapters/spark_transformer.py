from dataclasses import dataclass

from loguru import logger
from pyspark import StorageLevel
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DecimalType

from bank_etl.domain.models import (
    SourceData,
    TargetDataset,
    TargetTable,
    WarehouseData,
)
from bank_etl.ports.transformers import DataTransformer


@dataclass
class SparkDataTransformer(DataTransformer):
    max_valid_year: int

    def transform(self, source: SourceData) -> WarehouseData:
        logger.info("Applying source-to-target transformations")
        candidates = (
            (TargetTable.EDUCATION_STATUS, self._education(source.education_status)),
            (TargetTable.MARITAL_STATUS, self._marital(source.marital_status)),
            (
                TargetTable.MARKETING_CAMPAIGN,
                self._marketing_campaign(source.marketing_campaign),
            ),
            (TargetTable.CUSTOMERS, self._customers(source.bank_transactions)),
            (TargetTable.TRANSACTIONS, self._transactions(source.bank_transactions)),
        )

        datasets: list[TargetDataset] = []
        current_frame: DataFrame | None = None
        try:
            for table, frame in candidates:
                current_frame = frame
                frame.persist(StorageLevel.MEMORY_AND_DISK)
                row_count = frame.count()
                logger.info("Prepared {} rows for target {}", row_count, table.value)
                datasets.append(TargetDataset(table, frame, row_count))
                current_frame = None
        except Exception:
            if current_frame is not None:
                current_frame.unpersist(blocking=False)
            for dataset in datasets:
                dataset.frame.unpersist(blocking=False)
            raise

        return WarehouseData(tuple(datasets))

    @staticmethod
    def _education(frame: DataFrame) -> DataFrame:
        return frame.select("education_id", "value", "created_at", "updated_at")

    @staticmethod
    def _marital(frame: DataFrame) -> DataFrame:
        return frame.select("marital_id", "value", "created_at", "updated_at")

    @staticmethod
    def _marketing_campaign(frame: DataFrame) -> DataFrame:
        return frame.select(
            "loan_data_id",
            "age",
            "job",
            "marital_id",
            "education_id",
            "default",
            F.regexp_replace(F.col("balance"), r"[$,]", "").cast("int").alias("balance"),
            "housing",
            "loan",
            "contact",
            "day",
            "month",
            "duration",
            F.floor(F.col("duration") / F.lit(365)).cast("int").alias("duration_in_year"),
            "campaign",
            F.col("pdays").alias("days_since_last_campaign"),
            F.col("previous").alias("previous_campaign_contacts"),
            F.col("poutcome").alias("previous_campaign_outcome"),
            "subscribed_deposit",
            "created_at",
            "updated_at",
        )

    def _customers(self, frame: DataFrame) -> DataFrame:
        normalized_gender = F.upper(F.trim(F.col("CustGender")))
        gender = (
            F.when(normalized_gender == "M", F.lit("Male"))
            .when(normalized_gender == "F", F.lit("Female"))
            .otherwise(F.lit("Other"))
        )
        return (
            frame.select(
                F.trim(F.col("CustomerID")).alias("customer_id"),
                self._parse_legacy_date(F.col("CustomerDOB")).alias("birth_date"),
                gender.alias("gender"),
                F.trim(F.col("CustLocation")).alias("location"),
                F.col("CustAccountBalance").cast(DecimalType(18, 2)).alias("account_balance"),
            )
            .filter(self._is_present("customer_id"))
            .dropDuplicates(["customer_id"])
        )

    def _transactions(self, frame: DataFrame) -> DataFrame:
        raw_time = F.regexp_replace(F.trim(F.col("TransactionTime")), r"\D", "")
        padded_time = F.lpad(raw_time, 6, "0")
        transaction_time = F.when(
            F.length(raw_time).between(1, 6),
            F.concat_ws(
                ":",
                F.substring(padded_time, 1, 2),
                F.substring(padded_time, 3, 2),
                F.substring(padded_time, 5, 2),
            ),
        )
        return (
            frame.select(
                F.trim(F.col("TransactionID")).alias("transaction_id"),
                F.trim(F.col("CustomerID")).alias("customer_id"),
                self._parse_legacy_date(F.col("TransactionDate")).alias("transaction_date"),
                transaction_time.alias("transaction_time"),
                F.col("TransactionAmount (INR)")
                .cast(DecimalType(18, 2))
                .alias("transaction_amount"),
            )
            .filter(self._is_present("transaction_id") & self._is_present("customer_id"))
            .dropDuplicates(["transaction_id"])
        )

    def _parse_legacy_date(self, column: Column) -> Column:
        parsed = F.to_date(F.trim(column), "d/M/yy")
        return F.when(
            F.year(parsed) > self.max_valid_year,
            F.add_months(parsed, -1200),
        ).otherwise(parsed)

    @staticmethod
    def _is_present(column_name: str) -> Column:
        column = F.col(column_name)
        return column.isNotNull() & (column != "")
