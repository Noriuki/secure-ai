"""Amazon S3 storage adapter."""

from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from app.core.config import get_settings


class S3Storage:
    def __init__(self) -> None:
        settings = get_settings()
        self._bucket = settings.s3_bucket
        self._region = settings.aws_region
        if not self._bucket:
            raise RuntimeError(
                "S3_BUCKET is required. Create the bucket on AWS and set it in .env.",
            )
        self._client = boto3.client("s3", region_name=self._region)

    def save(
        self,
        key: str,
        data: bytes,
        *,
        metadata: dict[str, str] | None = None,
    ) -> str:
        extra: dict = {}
        if metadata:
            # S3 user metadata values must be strings.
            extra["Metadata"] = {k: str(v) for k, v in metadata.items()}
        self._client.put_object(Bucket=self._bucket, Key=key, Body=data, **extra)
        return key

    def read(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            if code in {"404", "NoSuchKey", "NotFound"}:
                raise FileNotFoundError(key) from exc
            raise
        body = response["Body"].read()
        return body if isinstance(body, bytes) else bytes(body)

    def delete(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)
