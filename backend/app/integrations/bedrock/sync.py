"""Trigger Knowledge Base ingestion after documents land in S3 and wait until done."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import boto3

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_TERMINAL = frozenset({"COMPLETE", "FAILED", "STOPPED"})
_POLL_INTERVAL_SECONDS = 3.0
_DEFAULT_TIMEOUT_SECONDS = 180.0


@dataclass(slots=True, frozen=True)
class KnowledgeBaseSyncResult:
    job_id: str | None
    status: str  # complete | failed | skipped | timeout


def sync_knowledge_base(*, timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS) -> KnowledgeBaseSyncResult:
    """Start an ingestion job and block until it finishes (or timeout)."""
    settings = get_settings()
    if not settings.bedrock_knowledge_base_id or not settings.bedrock_data_source_id:
        logger.warning(
            "KB sync skipped: set BEDROCK_KNOWLEDGE_BASE_ID and BEDROCK_DATA_SOURCE_ID",
        )
        return KnowledgeBaseSyncResult(job_id=None, status="skipped")

    client = boto3.client("bedrock-agent", region_name=settings.aws_region)
    response = client.start_ingestion_job(
        knowledgeBaseId=settings.bedrock_knowledge_base_id,
        dataSourceId=settings.bedrock_data_source_id,
    )
    job_id = response.get("ingestionJob", {}).get("ingestionJobId")
    if not job_id:
        logger.error("KB sync started without ingestionJobId")
        return KnowledgeBaseSyncResult(job_id=None, status="failed")

    logger.info("Started Bedrock ingestion job %s — waiting for completion", job_id)
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        job = client.get_ingestion_job(
            knowledgeBaseId=settings.bedrock_knowledge_base_id,
            dataSourceId=settings.bedrock_data_source_id,
            ingestionJobId=job_id,
        ).get("ingestionJob", {})
        status = str(job.get("status") or "")
        if status in _TERMINAL:
            mapped = "complete" if status == "COMPLETE" else "failed"
            logger.info("Bedrock ingestion job %s finished: %s", job_id, status)
            return KnowledgeBaseSyncResult(job_id=job_id, status=mapped)
        time.sleep(_POLL_INTERVAL_SECONDS)

    logger.error("Bedrock ingestion job %s timed out after %.0fs", job_id, timeout_seconds)
    return KnowledgeBaseSyncResult(job_id=job_id, status="timeout")
