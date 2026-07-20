"""Trigger Knowledge Base ingestion after documents land in S3."""

from __future__ import annotations

import logging

import boto3

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def start_knowledge_base_sync() -> str | None:
    """Start an ingestion job. Returns job id or None if not configured."""
    settings = get_settings()
    if not settings.bedrock_knowledge_base_id or not settings.bedrock_data_source_id:
        logger.warning(
            "KB sync skipped: set BEDROCK_KNOWLEDGE_BASE_ID and BEDROCK_DATA_SOURCE_ID",
        )
        return None

    client = boto3.client("bedrock-agent", region_name=settings.aws_region)
    response = client.start_ingestion_job(
        knowledgeBaseId=settings.bedrock_knowledge_base_id,
        dataSourceId=settings.bedrock_data_source_id,
    )
    job_id = response.get("ingestionJob", {}).get("ingestionJobId")
    logger.info("Started Bedrock ingestion job %s", job_id)
    return job_id
