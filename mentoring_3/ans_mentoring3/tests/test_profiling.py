from bank_etl.adapters.spark_change_detector import SparkBatchChangeDetector
from bank_etl.adapters.spark_profiler import SparkDataProfiler
from bank_etl.domain.models import (
    ProfileInput,
    ProfileStage,
    TargetDataset,
    TargetTable,
)
from bank_etl.infrastructure.config import DatabaseSettings, RetrySettings
from bank_etl.infrastructure.retry import RetryPolicy


def test_profiler_counts_nulls_and_duplicate_keys(spark) -> None:
    frame = spark.createDataFrame(
        [("A", "one"), ("A", None), ("B", "")],
        ["id", "value"],
    )

    profile = SparkDataProfiler().profile(
        (ProfileInput("sample", frame, ("id",)),),
        ProfileStage.SOURCE,
    )[0]

    assert profile.row_count == 3
    assert profile.column_count == 2
    assert profile.null_count == 2
    assert profile.null_by_column == {"id": 0, "value": 2}
    assert profile.duplicate_key_count == 1


def test_change_detector_classifies_snapshot_changes(spark, monkeypatch) -> None:
    current = spark.createDataFrame(
        [("A", "same"), ("B", "new"), ("C", "inserted")],
        ["customer_id", "location"],
    )
    previous = spark.createDataFrame(
        [("A", "same"), ("B", "old"), ("D", "deleted")],
        ["customer_id", "location"],
    )
    database = DatabaseSettings("unused", 5432, "unused", "unused", "unused", 1, 1)
    detector = SparkBatchChangeDetector(
        spark,
        database,
        RetryPolicy(RetrySettings(1, 0.01, 0.01)),
    )
    dataset = TargetDataset(TargetTable.CUSTOMERS, current, 3)
    monkeypatch.setattr(detector, "_table_row_count", lambda _table: 3)
    monkeypatch.setattr(detector, "_read_existing", lambda _dataset: previous)

    summary = detector._detect_dataset(dataset)

    assert summary.inserted_count == 1
    assert summary.updated_count == 1
    assert summary.deleted_count == 1
    assert summary.unchanged_count == 1
