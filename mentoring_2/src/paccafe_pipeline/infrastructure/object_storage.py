from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FailedDataPayload:
    layer: str
    job_name: str
    batch_id: str
    data: Any
    error_message: str


class ObjectStorageClient:
    """Object storage contract for failed-data dumps."""

    def dump_failed_data(self, payload: FailedDataPayload) -> str:
        """Persist failed data and return the object path."""
        raise NotImplementedError


class MinioObjectStorageClient(ObjectStorageClient):
    """MinIO adapter with local filesystem fallback."""

    def __init__(
        self,
        endpoint: str | None,
        access_key: str | None,
        secret_key: str | None,
        bucket_name: str,
        compose_directory: Path | None = None,
        fallback_directory: Path | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.compose_directory = compose_directory or Path("data_pipeline_paccafe")
        self.fallback_directory = fallback_directory or Path("data/failed")

    def dump_failed_data(self, payload: FailedDataPayload) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        object_key = f"{payload.layer}/{payload.job_name}/{payload.batch_id}/{timestamp}.json"
        document = {
            "layer": payload.layer,
            "job_name": payload.job_name,
            "batch_id": payload.batch_id,
            "error_message": payload.error_message,
            "data": payload.data,
            "dumped_at": timestamp,
        }
        json_payload = json.dumps(document, default=str, indent=2)

        if self._try_dump_to_minio(object_key, json_payload):
            return f"minio://{self.bucket_name}/{object_key}"

        return self._dump_to_local_file(object_key, json_payload)

    def _try_dump_to_minio(self, object_key: str, json_payload: str) -> bool:
        if not self.endpoint or not self.access_key or not self.secret_key:
            return False

        shell_command = (
            "mc alias set local http://127.0.0.1:9000 "
            f"{self.access_key} {self.secret_key} >/dev/null && "
            f"mc mb -p local/{self.bucket_name} >/dev/null 2>&1 || true; "
            f"mc pipe local/{self.bucket_name}/{object_key} >/dev/null"
        )
        command = [
            "docker",
            "compose",
            "exec",
            "-T",
            "minio",
            "sh",
            "-c",
            shell_command,
        ]
        result = subprocess.run(
            command,
            input=json_payload,
            text=True,
            capture_output=True,
            cwd=self.compose_directory,
            check=False,
        )
        return result.returncode == 0

    def _dump_to_local_file(self, object_key: str, json_payload: str) -> str:
        path = self.fallback_directory / self.bucket_name / object_key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json_payload, encoding="utf-8")
        return str(path)
