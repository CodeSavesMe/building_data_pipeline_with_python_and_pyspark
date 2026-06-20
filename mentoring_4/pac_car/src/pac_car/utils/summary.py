from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionSummary:
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None
    status: str = "RUNNING"
    extraction_rows: dict[str, int] = field(default_factory=dict)
    staging_rows: dict[str, int] = field(default_factory=dict)
    transformed_rows: int = 0
    rejected_rows: int = 0
    warehouse_rows: int = 0
    feature_columns: list[str] = field(default_factory=list)
    train_test_split: str | None = None
    algorithm: str | None = None
    model_metrics: dict[str, float] = field(default_factory=dict)
    artifact_file: str | None = None
    artifact_uri: str | None = None
    prediction_file: str | None = None
    prediction_uri: str | None = None
    error_message: str | None = None

    def mark_success(self) -> None:
        self.status = "SUCCESS"
        self.finished_at = datetime.now()

    def mark_failed(self, error_message: str) -> None:
        self.status = "FAILED"
        self.error_message = error_message
        self.finished_at = datetime.now()

    @property
    def duration_seconds(self) -> float:
        finished_at = self.finished_at or datetime.now()
        return (finished_at - self.started_at).total_seconds()

    def render(self) -> str:
        feature_names = ", ".join(self.feature_columns) if self.feature_columns else "-"
        lines = [
            "",
            "========== PAC CAR PIPELINE SUMMARY ==========",
            f"Started at       : {self.started_at:%Y-%m-%d %H:%M:%S}",
            f"Duration seconds : {self.duration_seconds:.2f}",
            f"Final status     : {self.status}",
            "",
            "[Extraction]",
            *_render_key_values(self.extraction_rows, suffix=" rows"),
            "",
            "[Staging]",
            *_render_key_values(self.staging_rows, suffix=" rows"),
            "",
            "[Transformation]",
            f"Processed rows   : {self.transformed_rows + self.rejected_rows}",
            f"Loaded rows      : {self.transformed_rows}",
            f"Rejected rows    : {self.rejected_rows}",
            f"Warehouse rows   : {self.warehouse_rows}",
            "",
            "[Machine Learning]",
            f"Features         : {feature_names}",
            f"Train/test split : {self.train_test_split or '-'}",
            f"Algorithm        : {self.algorithm or '-'}",
            *_render_metric_values(self.model_metrics),
            f"Artifact file    : {self.artifact_file or '-'}",
            f"Artifact URI     : {self.artifact_uri or '-'}",
            f"Prediction file  : {self.prediction_file or '-'}",
            f"Prediction URI   : {self.prediction_uri or '-'}",
        ]

        if self.error_message:
            lines.extend(["", "[Error]", self.error_message])

        lines.append("==============================================")
        return "\n".join(lines)


def _render_key_values(values: dict[str, int], *, suffix: str) -> list[str]:
    if not values:
        return ["-"]
    return [f"{key:<16}: {value}{suffix}" for key, value in values.items()]


def _render_metric_values(metrics: dict[str, float]) -> list[str]:
    if not metrics:
        return ["Metrics          : -"]
    return [f"{key:<16}: {value:.4f}" for key, value in metrics.items()]
