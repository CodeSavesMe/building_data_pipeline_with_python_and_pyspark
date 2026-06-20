from __future__ import annotations

import logging
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from pac_car.config.settings import MinioSettings


class MinioClient:
    """Uploads model artifacts to MinIO-compatible object storage."""

    def __init__(self, settings: MinioSettings, logger: logging.Logger) -> None:
        self._settings = settings
        self._logger = logger
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.endpoint_url,
            aws_access_key_id=settings.access_key,
            aws_secret_access_key=settings.secret_key,
        )

    @property
    def bucket_name(self) -> str:
        return self._settings.bucket_name

    def upload_file(self, file_path: Path, object_name: str) -> str:
        self._ensure_bucket_exists()
        self._logger.info("Uploading file to MinIO: %s/%s", self.bucket_name, object_name)
        self._client.upload_file(str(file_path), self.bucket_name, object_name)
        return f"s3://{self.bucket_name}/{object_name}"

    def _ensure_bucket_exists(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket_name)
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code")
            if error_code not in {"404", "NoSuchBucket"}:
                raise
            self._logger.info("Creating MinIO bucket: %s", self.bucket_name)
            self._client.create_bucket(Bucket=self.bucket_name)
