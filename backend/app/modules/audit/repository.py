from uuid import UUID, uuid4

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditEvent
from app.modules.conversations.models import Conversation, Message
from app.modules.documents.models import Document
from app.modules.workspaces.models import Workspace
from app.shared.schemas import TimestampMixin


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(
        self,
        *,
        event_type: str,
        workspace_id: UUID | None = None,
        conversation_id: UUID | None = None,
        document_id: UUID | None = None,
        message_id: UUID | None = None,
        model: str | None = None,
        latency_ms: int | None = None,
        pii_match_count: int = 0,
        source_count: int = 0,
        estimated_cost_usd: float | None = None,
        detail: str | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=uuid4(),
            event_type=event_type,
            workspace_id=workspace_id,
            conversation_id=conversation_id,
            document_id=document_id,
            message_id=message_id,
            model=model,
            latency_ms=latency_ms,
            pii_match_count=pii_match_count,
            source_count=source_count,
            estimated_cost_usd=estimated_cost_usd,
            detail=detail,
            created_at=TimestampMixin.utcnow(),
        )
        self._db.add(event)
        self._db.commit()
        self._db.refresh(event)
        return event

    def list_recent(self, *, limit: int = 30) -> list[AuditEvent]:
        stmt: Select[tuple[AuditEvent]] = (
            select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
        )
        return list(self._db.scalars(stmt).all())

    def dashboard_counts(self) -> dict:
        workspaces = self._db.scalar(select(func.count()).select_from(Workspace)) or 0
        documents = self._db.scalar(select(func.count()).select_from(Document)) or 0
        conversations = self._db.scalar(select(func.count()).select_from(Conversation)) or 0
        messages = self._db.scalar(select(func.count()).select_from(Message)) or 0

        llm_calls = (
            self._db.scalar(
                select(func.count()).select_from(AuditEvent).where(AuditEvent.event_type == "chat")
            )
            or 0
        )
        avg_latency = self._db.scalar(
            select(func.avg(AuditEvent.latency_ms)).where(
                AuditEvent.event_type == "chat",
                AuditEvent.latency_ms.is_not(None),
            )
        )
        pii_detections = (
            self._db.scalar(
                select(func.coalesce(func.sum(AuditEvent.pii_match_count), 0)),
            )
            or 0
        )
        estimated_cost = self._db.scalar(
            select(func.coalesce(func.sum(AuditEvent.estimated_cost_usd), 0.0)).where(
                AuditEvent.estimated_cost_usd.is_not(None),
            )
        )

        return {
            "workspaces": int(workspaces),
            "documents": int(documents),
            "conversations": int(conversations),
            "messages": int(messages),
            "llm_calls": int(llm_calls),
            "avg_latency_ms": int(avg_latency) if avg_latency is not None else None,
            "pii_detections": int(pii_detections),
            "estimated_cost_usd": round(float(estimated_cost or 0), 6),
        }
