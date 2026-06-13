from collections.abc import Iterator
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class SourceTable(StrEnum):
    EDUCATION_STATUS = "education_status"
    MARITAL_STATUS = "marital_status"
    MARKETING_CAMPAIGN = "marketing_campaign_deposit"


class TargetTable(StrEnum):
    EDUCATION_STATUS = "education_status"
    MARITAL_STATUS = "marital_status"
    MARKETING_CAMPAIGN = "marketing_campaign_deposit"
    CUSTOMERS = "customers"
    TRANSACTIONS = "transactions"


class ProfileStage(StrEnum):
    SOURCE = "source"
    TARGET = "target"


LOAD_ORDER = (
    TargetTable.EDUCATION_STATUS,
    TargetTable.MARITAL_STATUS,
    TargetTable.MARKETING_CAMPAIGN,
    TargetTable.CUSTOMERS,
    TargetTable.TRANSACTIONS,
)

TARGET_KEY_COLUMNS = {
    TargetTable.EDUCATION_STATUS: ("education_id",),
    TargetTable.MARITAL_STATUS: ("marital_id",),
    TargetTable.MARKETING_CAMPAIGN: ("loan_data_id",),
    TargetTable.CUSTOMERS: ("customer_id",),
    TargetTable.TRANSACTIONS: ("transaction_id",),
}


@dataclass(frozen=True)
class ProfileInput:
    dataset_name: str
    frame: Any
    key_columns: tuple[str, ...]


@dataclass(frozen=True)
class SourceData:
    education_status: Any
    marital_status: Any
    marketing_campaign: Any
    bank_transactions: Any

    def frames(self) -> Iterator[Any]:
        yield self.education_status
        yield self.marital_status
        yield self.marketing_campaign
        yield self.bank_transactions

    def profile_inputs(self) -> tuple[ProfileInput, ...]:
        return (
            ProfileInput("education_status", self.education_status, ("education_id",)),
            ProfileInput("marital_status", self.marital_status, ("marital_id",)),
            ProfileInput(
                "marketing_campaign_deposit",
                self.marketing_campaign,
                ("loan_data_id",),
            ),
            ProfileInput(
                "new_bank_transactions.csv",
                self.bank_transactions,
                ("TransactionID",),
            ),
        )


@dataclass(frozen=True)
class TargetDataset:
    table: TargetTable
    frame: Any
    row_count: int


@dataclass(frozen=True)
class WarehouseData:
    datasets: tuple[TargetDataset, ...]

    def __post_init__(self) -> None:
        actual_order = tuple(dataset.table for dataset in self.datasets)
        if actual_order != LOAD_ORDER:
            expected = ", ".join(table.value for table in LOAD_ORDER)
            raise ValueError(f"Warehouse datasets must use this load order: {expected}")

    def frames(self) -> Iterator[Any]:
        for dataset in self.datasets:
            yield dataset.frame

    def profile_inputs(self) -> tuple[ProfileInput, ...]:
        return tuple(
            ProfileInput(
                dataset.table.value,
                dataset.frame,
                TARGET_KEY_COLUMNS[dataset.table],
            )
            for dataset in self.datasets
        )


@dataclass(frozen=True)
class DataProfile:
    stage: ProfileStage
    dataset_name: str
    row_count: int
    column_count: int
    null_count: int
    duplicate_key_count: int
    null_by_column: dict[str, int]


@dataclass(frozen=True)
class ChangeSummary:
    table: TargetTable
    inserted_count: int
    updated_count: int
    deleted_count: int
    unchanged_count: int
