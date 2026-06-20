from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import reduce

import pandas as pd
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession
from pyspark.sql import functions as spark_functions
from pyspark.sql.column import Column


@dataclass(frozen=True)
class TransformResult:
    dataframe: pd.DataFrame
    processed_rows: int
    rejected_rows: int


class CarSalesTransformer:
    """Cleans raw sales data and maps external references into warehouse keys."""

    TEXT_COLUMNS = ["brand_car", "transmission", "state", "color", "interior"]
    NULL_TOKENS = ("", "-", "\u2014", "nan", "none", "null", "<na>")
    OUTPUT_COLUMNS = [
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
        logger: logging.Logger,
        spark_session: SparkSession | None = None,
        *,
        spark_master_url: str | None = None,
    ) -> None:
        self._logger = logger
        self._spark_master_url = spark_master_url
        self._spark = spark_session or self._create_spark_session()

    def transform(
        self,
        sales_dataframe: pd.DataFrame,
        brand_dataframe: pd.DataFrame,
        state_dataframe: pd.DataFrame,
    ) -> TransformResult:
        self._logger.info("Transforming sales data with PySpark")

        sales_spark = self._spark.createDataFrame(_stringify_dataframe(sales_dataframe))
        brand_spark = self._spark.createDataFrame(brand_dataframe)
        state_spark = self._spark.createDataFrame(state_dataframe)

        processed_rows = sales_spark.count()
        cleaned_sales = self._prepare_sales(sales_spark)
        prepared_brands = self._prepare_brands(brand_spark)
        prepared_states = self._prepare_states(state_spark)

        joined_sales = cleaned_sales.join(prepared_brands, on="brand_join_key", how="left").join(
            prepared_states, on="state_join_key", how="left"
        )

        valid_sales = self._filter_valid_sales(joined_sales)
        transformed_spark = valid_sales.select(*self.OUTPUT_COLUMNS).dropDuplicates(["id_sales_nk"])
        transformed_dataframe = transformed_spark.toPandas()
        rejected_rows = processed_rows - len(transformed_dataframe)

        self._logger.info(
            "Transformation finished: processed=%s, loaded=%s, rejected=%s",
            processed_rows,
            len(transformed_dataframe),
            rejected_rows,
        )
        return TransformResult(
            dataframe=transformed_dataframe,
            processed_rows=processed_rows,
            rejected_rows=rejected_rows,
        )

    def stop(self) -> None:
        self._spark.stop()

    def _prepare_sales(self, dataframe: SparkDataFrame) -> SparkDataFrame:
        cleaned = dataframe.select(
            spark_functions.col("id_sales").cast("int").alias("id_sales_nk"),
            spark_functions.col("year").cast("int").alias("year"),
            self._clean_text("brand_car").alias("brand_car"),
            self._clean_text("transmission").alias("transmission"),
            self._clean_text("state").alias("state"),
            spark_functions.col("condition").cast("float").alias("condition"),
            spark_functions.col("odometer").cast("float").alias("odometer"),
            self._clean_text("color").alias("color"),
            self._clean_text("interior").alias("interior"),
            spark_functions.col("mmr").cast("float").alias("mmr"),
            spark_functions.col("sellingprice").cast("float").alias("selling_price"),
        )
        return cleaned.withColumn(
            "brand_join_key",
            spark_functions.lower(spark_functions.trim(spark_functions.col("brand_car"))),
        ).withColumn(
            "state_join_key",
            spark_functions.lower(spark_functions.trim(spark_functions.col("state"))),
        )

    def _prepare_brands(self, dataframe: SparkDataFrame) -> SparkDataFrame:
        return dataframe.select(
            spark_functions.col("brand_car_id").cast("int").alias("brand_car_id"),
            spark_functions.lower(spark_functions.trim(spark_functions.col("brand_name"))).alias(
                "brand_join_key"
            ),
        )

    def _prepare_states(self, dataframe: SparkDataFrame) -> SparkDataFrame:
        return dataframe.select(
            spark_functions.col("id_state").cast("int").alias("id_state"),
            spark_functions.lower(spark_functions.trim(spark_functions.col("code"))).alias(
                "state_join_key"
            ),
        )

    def _filter_valid_sales(self, dataframe: SparkDataFrame) -> SparkDataFrame:
        required_columns = [
            "id_sales_nk",
            "year",
            "brand_car_id",
            "id_state",
            "condition",
            "odometer",
            "mmr",
            "selling_price",
        ]
        required_filter = reduce(
            lambda left, right: left & right,
            [spark_functions.col(column).isNotNull() for column in required_columns],
        )
        numeric_filter = (
            (spark_functions.col("year") >= 1980)
            & (spark_functions.col("odometer") >= 0)
            & (spark_functions.col("mmr") > 0)
            & (spark_functions.col("selling_price") > 0)
        )
        return dataframe.filter(required_filter & numeric_filter)

    def _clean_text(self, column_name: str) -> Column:
        cleaned_column = spark_functions.trim(spark_functions.col(column_name).cast("string"))
        return spark_functions.when(
            spark_functions.lower(cleaned_column).isin(*self.NULL_TOKENS),
            spark_functions.lit(None),
        ).otherwise(cleaned_column)

    def _create_spark_session(self) -> SparkSession:
        builder = SparkSession.builder.appName("pac-car-transformer").config(
            "spark.sql.execution.arrow.pyspark.enabled",
            "true",
        )
        builder = (
            builder.config("spark.driver.bindAddress", "0.0.0.0")
            .config("spark.executorEnv.PYSPARK_PYTHON", "python")
            .config("spark.executorEnv.PYSPARK_DRIVER_PYTHON", "python")
        )
        if self._spark_master_url:
            builder = builder.master(self._spark_master_url)
        else:
            builder = builder.master("local[*]")

        spark = builder.getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        return spark


def _stringify_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.astype("string").fillna("")
