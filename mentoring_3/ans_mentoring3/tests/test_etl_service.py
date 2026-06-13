from pathlib import Path

from bank_etl.application.etl_service import ETLService
from bank_etl.domain.models import (
    LOAD_ORDER,
    ChangeSummary,
    DataProfile,
    ProfileStage,
    SourceData,
    SourceTable,
    TargetDataset,
    WarehouseData,
)


class FakeFrame:
    def __init__(self, name: str) -> None:
        self.name = name
        self.released = False

    def unpersist(self, blocking: bool) -> None:
        assert blocking is False
        self.released = True


class FakeDatabaseReader:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def read_table(self, table: SourceTable) -> FakeFrame:
        self.calls.append(f"read:{table.value}")
        return FakeFrame(table.value)


class FakeFileReader:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def read_csv(self, path: Path) -> FakeFrame:
        self.calls.append(f"read:{path.name}")
        return FakeFrame(path.name)


class FakeTransformer:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def transform(self, source: SourceData) -> WarehouseData:
        self.calls.append("transform")
        datasets = tuple(TargetDataset(table, FakeFrame(table.value), 1) for table in LOAD_ORDER)
        return WarehouseData(datasets)


class FakeProfiler:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def profile(self, datasets, stage: ProfileStage) -> tuple[DataProfile, ...]:
        self.calls.append(f"profile:{stage.value}")
        return tuple(
            DataProfile(stage, dataset.dataset_name, 1, 1, 0, 0, {}) for dataset in datasets
        )


class FakeChangeDetector:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def detect(self, data: WarehouseData) -> tuple[ChangeSummary, ...]:
        self.calls.append("detect_changes")
        return tuple(ChangeSummary(dataset.table, 1, 0, 0, 0) for dataset in data.datasets)


class FakeWriter:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def replace_all(self, data: WarehouseData) -> None:
        self.calls.append("load")
        assert tuple(dataset.table for dataset in data.datasets) == LOAD_ORDER


class FakeAuditRepository:
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def start_run(self) -> str:
        self.calls.append("audit:start")
        return "run-1"

    def save_profiles(self, run_id: str, profiles) -> None:
        assert run_id == "run-1"
        self.calls.append(f"audit:profiles:{profiles[0].stage.value}")

    def save_changes(self, run_id: str, changes) -> None:
        assert run_id == "run-1"
        self.calls.append("audit:changes")

    def mark_succeeded(self, run_id: str, duration_seconds: float) -> None:
        assert run_id == "run-1"
        assert duration_seconds >= 0
        self.calls.append("audit:succeeded")

    def mark_failed(self, run_id: str, error_message: str) -> None:
        self.calls.append("audit:failed")

    def export_summary(self, run_id: str, path: Path) -> None:
        assert run_id == "run-1"
        self.calls.append(f"audit:export:{path.name}")


def test_etl_service_runs_hexagonal_ports_in_sequence() -> None:
    calls: list[str] = []
    service = ETLService(
        database_reader=FakeDatabaseReader(calls),
        file_reader=FakeFileReader(calls),
        transformer=FakeTransformer(calls),
        profiler=FakeProfiler(calls),
        change_detector=FakeChangeDetector(calls),
        warehouse_writer=FakeWriter(calls),
        audit_repository=FakeAuditRepository(calls),
        csv_path=Path("new_bank_transactions.csv"),
        profile_report_path=Path("latest_profile_summary.json"),
    )

    service.run()

    assert calls == [
        "audit:start",
        "read:education_status",
        "read:marital_status",
        "read:marketing_campaign_deposit",
        "read:new_bank_transactions.csv",
        "profile:source",
        "audit:profiles:source",
        "transform",
        "profile:target",
        "audit:profiles:target",
        "detect_changes",
        "audit:changes",
        "load",
        "audit:succeeded",
        "audit:export:latest_profile_summary.json",
    ]
