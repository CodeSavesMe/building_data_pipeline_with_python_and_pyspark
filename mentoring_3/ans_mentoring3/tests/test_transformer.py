from datetime import date, datetime
from decimal import Decimal

from pyspark.sql.types import (
    BooleanType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from bank_etl.adapters.spark_transformer import SparkDataTransformer


def test_customers_apply_date_gender_decimal_and_deduplication(spark) -> None:
    schema = StructType(
        [
            StructField("CustomerID", StringType()),
            StructField("CustomerDOB", StringType()),
            StructField("CustGender", StringType()),
            StructField("CustLocation", StringType()),
            StructField("CustAccountBalance", StringType()),
        ]
    )
    frame = spark.createDataFrame(
        [
            ("C1", "1/1/30", "M", "Jakarta", "1000.50"),
            ("C1", "1/1/30", "M", "Jakarta", "1000.50"),
            ("C2", "21/6/65", "F", "Bandung", "25"),
            ("C3", "2/2/01", None, "Surabaya", "0"),
            (None, "1/1/90", "M", "Bogor", "10"),
        ],
        schema,
    )

    rows = {
        row.customer_id: row
        for row in SparkDataTransformer(max_valid_year=2025)._customers(frame).collect()
    }

    assert set(rows) == {"C1", "C2", "C3"}
    assert rows["C1"].birth_date == date(1930, 1, 1)
    assert rows["C2"].birth_date == date(1965, 6, 21)
    assert rows["C1"].gender == "Male"
    assert rows["C2"].gender == "Female"
    assert rows["C3"].gender == "Other"
    assert rows["C1"].account_balance == Decimal("1000.50")


def test_transactions_format_date_time_and_amount(spark) -> None:
    schema = StructType(
        [
            StructField("TransactionID", StringType()),
            StructField("CustomerID", StringType()),
            StructField("TransactionDate", StringType()),
            StructField("TransactionTime", StringType()),
            StructField("TransactionAmount (INR)", StringType()),
        ]
    )
    frame = spark.createDataFrame(
        [
            ("T1", "C1", "18/8/16", "141103", "5000"),
            ("T2", "C2", "1/1/30", "923", "10.25"),
            ("T2", "C2", "1/1/30", "923", "10.25"),
        ],
        schema,
    )

    rows = {
        row.transaction_id: row for row in SparkDataTransformer(2025)._transactions(frame).collect()
    }

    assert set(rows) == {"T1", "T2"}
    assert rows["T1"].transaction_date == date(2016, 8, 18)
    assert rows["T1"].transaction_time == "14:11:03"
    assert rows["T2"].transaction_date == date(1930, 1, 1)
    assert rows["T2"].transaction_time == "00:09:23"
    assert rows["T2"].transaction_amount == Decimal("10.25")


def test_marketing_campaign_applies_source_to_target_mapping(spark) -> None:
    timestamp = datetime(2025, 2, 28, 15, 59, 11)
    schema = StructType(
        [
            StructField("loan_data_id", IntegerType()),
            StructField("age", IntegerType()),
            StructField("job", StringType()),
            StructField("marital_id", IntegerType()),
            StructField("education_id", IntegerType()),
            StructField("default", BooleanType()),
            StructField("balance", StringType()),
            StructField("housing", BooleanType()),
            StructField("loan", BooleanType()),
            StructField("contact", StringType()),
            StructField("day", IntegerType()),
            StructField("month", StringType()),
            StructField("duration", IntegerType()),
            StructField("campaign", IntegerType()),
            StructField("pdays", IntegerType()),
            StructField("previous", IntegerType()),
            StructField("poutcome", StringType()),
            StructField("subscribed_deposit", BooleanType()),
            StructField("created_at", TimestampType()),
            StructField("updated_at", TimestampType()),
        ]
    )
    frame = spark.createDataFrame(
        [
            (
                1,
                40,
                "admin",
                1,
                2,
                False,
                "$-1,372",
                True,
                False,
                "cellular",
                5,
                "may",
                730,
                1,
                20,
                3,
                "success",
                True,
                timestamp,
                timestamp,
            )
        ],
        schema,
    )

    row = SparkDataTransformer._marketing_campaign(frame).first()

    assert row.balance == -1372
    assert row.duration_in_year == 2
    assert row.days_since_last_campaign == 20
    assert row.previous_campaign_contacts == 3
    assert row.previous_campaign_outcome == "success"
