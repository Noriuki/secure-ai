from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.documents.models import Document
from app.shared.schemas import TimestampMixin


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_workspace(self, workspace_id: UUID) -> list[Document]:
        stmt = (
            select(Document)
            .where(
                Document.workspace_id == workspace_id,
                Document.status == "ready",
            )
            .order_by(Document.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get_in_workspace(self, workspace_id: UUID, document_id: UUID) -> Document | None:
        stmt = select(Document).where(
            Document.id == document_id,
            Document.workspace_id == workspace_id,
        )
        return self._db.scalars(stmt).first()

    def create(
        self,
        *,
        workspace_id: UUID,
        filename: str,
        content_type: str,
        size_bytes: int,
        storage_key: str,
        status: str = "uploaded",
        document_id: UUID | None = None,
        kb_sync_job_id: str | None = None,
        kb_sync_status: str | None = None,
    ) -> Document:
        now = TimestampMixin.utcnow()
        document = Document(
            id=document_id or uuid4(),
            workspace_id=workspace_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
            storage_key=storage_key,
            status=status,
            kb_sync_job_id=kb_sync_job_id,
            kb_sync_status=kb_sync_status,
            created_at=now,
            updated_at=now,
        )
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self._db.delete(document)
        self._db.commit()
