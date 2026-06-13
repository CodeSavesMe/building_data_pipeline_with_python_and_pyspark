from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

from loguru import logger

from bank_etl.domain.models import ProfileStage, SourceData, SourceTable, WarehouseData
from bank_etl.ports.audit import RunAuditRepository
from bank_etl.ports.profiling import ChangeDetector, DataProfiler
from bank_etl.ports.readers import SourceDatabaseReader, SourceFileReader
from bank_etl.ports.transformers import DataTransformer
from bank_etl.ports.writers import WarehouseWriter


@dataclass
class ETLService:
    database_reader: SourceDatabaseReader
    file_reader: SourceFileReader
    transformer: DataTransformer
    profiler: DataProfiler
    change_detector: ChangeDetector
    warehouse_writer: WarehouseWriter
    audit_repository: RunAuditRepository
    csv_path: Path
    profile_report_path: Path

    def run(self) -> None:
        started_at = perf_counter()
        source: SourceData | None = None
        transformed: WarehouseData | None = None
        run_id = self.audit_repository.start_run()
        logger.info("ETL pipeline started with run_id={}", run_id)

        try:
            source = self._extract()
            source_profiles = self.profiler.profile(source.profile_inputs(), ProfileStage.SOURCE)
            self.audit_repository.save_profiles(run_id, source_profiles)

            transformed = self._transform(source)
            target_profiles = self.profiler.profile(
                transformed.profile_inputs(), ProfileStage.TARGET
            )
            self.audit_repository.save_profiles(run_id, target_profiles)

            changes = self.change_detector.detect(transformed)
            self.audit_repository.save_changes(run_id, changes)

            self._load(transformed)
            duration_seconds = perf_counter() - started_at
            self.audit_repository.mark_succeeded(run_id, duration_seconds)
            self.audit_repository.export_summary(run_id, self.profile_report_path)
            logger.info("ETL pipeline completed in {:.2f} seconds", duration_seconds)
        except Exception as error:
            logger.exception("ETL pipeline run {} failed", run_id)
            try:
                self.audit_repository.mark_failed(run_id, str(error))
                self.audit_repository.export_summary(run_id, self.profile_report_path)
            except Exception as audit_error:
                logger.exception("Failed to finalize audit run {}: {}", run_id, audit_error)
            raise
        finally:
            self._unpersist(source.frames() if source else ())
            self._unpersist(transformed.frames() if transformed else ())

    def _extract(self) -> SourceData:
        logger.info("Extract phase started")
        source = SourceData(
            education_status=self.database_reader.read_table(SourceTable.EDUCATION_STATUS),
            marital_status=self.database_reader.read_table(SourceTable.MARITAL_STATUS),
            marketing_campaign=self.database_reader.read_table(SourceTable.MARKETING_CAMPAIGN),
            bank_transactions=self.file_reader.read_csv(self.csv_path),
        )
        logger.info("Extract phase completed")
        return source

    def _transform(self, source: SourceData) -> WarehouseData:
        logger.info("Transform phase started")
        transformed = self.transformer.transform(source)
        logger.info("Transform phase completed")
        return transformed

    def _load(self, transformed: WarehouseData) -> None:
        logger.info("Load phase started")
        self.warehouse_writer.replace_all(transformed)
        logger.info("Load phase completed")

    @staticmethod
    def _unpersist(frames: Any) -> None:
        for frame in frames:
            try:
                frame.unpersist(blocking=False)
            except Exception as error:
                logger.warning("Failed to release cached Spark DataFrame: {}", error)
