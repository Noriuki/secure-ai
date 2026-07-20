from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditEventResponse, DashboardResponse


def estimate_chat_cost_usd(*, latency_ms: int | None, source_count: int) -> float:
    """Rough portfolio estimate (not AWS billing)."""
    base = 0.0008
    latency_factor = (latency_ms or 0) / 60_000
    return round(base + (0.00015 * max(source_count, 0)) + latency_factor * 0.001, 6)


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self._repository = repository

    def record_chat(
        self,
        *,
        workspace_id: UUID,
        conversation_id: UUID,
        message_id: UUID,
        model: str | None,
        latency_ms: int | None,
        pii_match_count: int,
        source_count: int,
    ):
        cost = estimate_chat_cost_usd(latency_ms=latency_ms, source_count=source_count)
        return self._repository.create(
            event_type="chat",
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            message_id=message_id,
            model=model,
            latency_ms=latency_ms,
            pii_match_count=pii_match_count,
            source_count=source_count,
            estimated_cost_usd=cost,
        )

    def record_upload(
        self,
        *,
        workspace_id: UUID,
        document_id: UUID,
        pii_match_count: int,
        detail: str | None = None,
    ):
        return self._repository.create(
            event_type="upload",
            workspace_id=workspace_id,
            document_id=document_id,
            pii_match_count=pii_match_count,
            detail=detail,
        )

    def record_kb_sync(
        self,
        *,
        workspace_id: UUID,
        document_id: UUID,
        job_id: str | None,
        status: str,
    ):
        return self._repository.create(
            event_type="kb_sync",
            workspace_id=workspace_id,
            document_id=document_id,
            detail=f"status={status}; job_id={job_id or '-'}",
        )

    def dashboard(self) -> DashboardResponse:
        counts = self._repository.dashboard_counts()
        recent = [
            AuditEventResponse.model_validate(event)
            for event in self._repository.list_recent(limit=25)
        ]
        return DashboardResponse(**counts, recent_events=recent)


def get_audit_service(db: Annotated[Session, Depends(get_db)]) -> AuditService:
    return AuditService(AuditRepository(db))
