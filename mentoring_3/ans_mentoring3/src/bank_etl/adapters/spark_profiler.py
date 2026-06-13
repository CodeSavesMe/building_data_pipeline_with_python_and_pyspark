from dataclasses import dataclass

from loguru import logger
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from bank_etl.domain.models import DataProfile, ProfileInput, ProfileStage
from bank_etl.ports.profiling import DataProfiler


@dataclass
class SparkDataProfiler(DataProfiler):
    def profile(
        self,
        datasets: tuple[ProfileInput, ...],
        stage: ProfileStage,
    ) -> tuple[DataProfile, ...]:
        logger.info("{} data profiling started", stage.value.capitalize())
        profiles = tuple(self._profile_dataset(dataset, stage) for dataset in datasets)
        logger.info("{} data profiling completed", stage.value.capitalize())
        return profiles

    def _profile_dataset(
        self,
        dataset: ProfileInput,
        stage: ProfileStage,
    ) -> DataProfile:
        frame: DataFrame = dataset.frame
        null_expressions = [
            F.sum(
                F.when(
                    F.col(column).isNull() | (F.trim(F.col(column).cast("string")) == ""),
                    1,
                ).otherwise(0)
            ).alias(column)
            for column in frame.columns
        ]
        metrics = frame.agg(F.count(F.lit(1)).alias("_row_count"), *null_expressions).first()
        null_by_column = {column: int(metrics[column] or 0) for column in frame.columns}
        duplicate_key_count = self._duplicate_key_count(frame, dataset.key_columns)
        profile = DataProfile(
            stage=stage,
            dataset_name=dataset.dataset_name,
            row_count=int(metrics["_row_count"]),
            column_count=len(frame.columns),
            null_count=sum(null_by_column.values()),
            duplicate_key_count=duplicate_key_count,
            null_by_column=null_by_column,
        )
        logger.info(
            "Profiled {} {}: rows={}, columns={}, nulls={}, duplicate_keys={}",
            stage.value,
            dataset.dataset_name,
            profile.row_count,
            profile.column_count,
            profile.null_count,
            profile.duplicate_key_count,
        )
        return profile

    @staticmethod
    def _duplicate_key_count(frame: DataFrame, key_columns: tuple[str, ...]) -> int:
        return frame.groupBy(*key_columns).count().filter(F.col("count") > 1).count()
