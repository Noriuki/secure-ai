from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.shared.schemas import OrmModel


class AuditEventResponse(OrmModel):
    id: UUID
    workspace_id: UUID | None
    conversation_id: UUID | None
    document_id: UUID | None
    message_id: UUID | None
    event_type: str
    model: str | None
    latency_ms: int | None
    pii_match_count: int
    source_count: int
    estimated_cost_usd: float | None
    detail: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DashboardResponse(BaseModel):
    workspaces: int
    documents: int
    conversations: int
    messages: int
    llm_calls: int
    avg_latency_ms: int | None
    pii_detections: int
    estimated_cost_usd: float
    recent_events: list[AuditEventResponse]
