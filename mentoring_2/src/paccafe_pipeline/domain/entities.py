from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass(frozen=True)
class BatchContext:
    """Metadata shared by jobs in one pipeline run."""

    batch_id: str
    started_at: datetime

    @classmethod
    def create(cls) -> "BatchContext":
        return cls(batch_id=str(uuid4()), started_at=datetime.now(timezone.utc))
