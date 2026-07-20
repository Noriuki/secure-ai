from uuid import UUID

from app.shared.schemas import OrmModel, TimestampMixin


class DocumentResponse(OrmModel, TimestampMixin):
    id: UUID
    workspace_id: UUID
    filename: str
    content_type: str
    size_bytes: int
    storage_key: str
    status: str
    kb_sync_job_id: str | None = None
    kb_sync_status: str | None = None
