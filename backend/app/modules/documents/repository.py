from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.documents.models import Document
from app.shared.schemas import TimestampMixin


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_workspace(self, workspace_id: UUID) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.workspace_id == workspace_id)
            .order_by(Document.created_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get(self, document_id: UUID) -> Document | None:
        return self._db.get(Document, document_id)

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
            created_at=now,
            updated_at=now,
        )
        self._db.add(document)
        self._db.commit()
        self._db.refresh(document)
        return document

    def update_status(
        self,
        document_id: UUID,
        status: str,
        *,
        kb_sync_job_id: str | None = None,
        kb_sync_status: str | None = None,
        size_bytes: int | None = None,
        storage_key: str | None = None,
        content_type: str | None = None,
    ) -> Document:
        document = self.get(document_id)
        if document is None:
            raise NotFoundError(f"Document {document_id} not found")
        document.status = status
        if kb_sync_job_id is not None:
            document.kb_sync_job_id = kb_sync_job_id
        if kb_sync_status is not None:
            document.kb_sync_status = kb_sync_status
        if size_bytes is not None:
            document.size_bytes = size_bytes
        if storage_key is not None:
            document.storage_key = storage_key
        if content_type is not None:
            document.content_type = content_type
        document.updated_at = TimestampMixin.utcnow()
        self._db.commit()
        self._db.refresh(document)
        return document

    def delete(self, document: Document) -> None:
        self._db.delete(document)
        self._db.commit()
