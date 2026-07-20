import logging
from pathlib import PurePosixPath
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import NotFoundError, ValidationAppError
from app.core.security.service import PiiService, get_pii_service
from app.core.storage import StoragePort, get_storage
from app.integrations.bedrock.sync import start_knowledge_base_sync
from app.integrations.documents.pdf import extract_text_from_pdf
from app.modules.audit.service import AuditService, get_audit_service
from app.modules.documents.models import Document
from app.modules.documents.repository import DocumentRepository
from app.modules.workspaces.repository import WorkspaceRepository

logger = logging.getLogger(__name__)

_TEXT_SUFFIXES = (".txt", ".md", ".csv")


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        storage: StoragePort,
        pii_service: PiiService,
        audit_service: AuditService,
    ) -> None:
        self._repository = repository
        self._workspace_repository = workspace_repository
        self._storage = storage
        self._pii_service = pii_service
        self._audit = audit_service

    def _ensure_workspace(self, workspace_id: UUID) -> None:
        if self._workspace_repository.get(workspace_id) is None:
            raise NotFoundError(f"Workspace {workspace_id} not found")

    def list_documents(self, workspace_id: UUID) -> list[Document]:
        self._ensure_workspace(workspace_id)
        return self._repository.list_by_workspace(workspace_id)

    def get_document(self, workspace_id: UUID, document_id: UUID) -> Document:
        self._ensure_workspace(workspace_id)
        document = self._repository.get_in_workspace(workspace_id, document_id)
        if document is None:
            raise NotFoundError(f"Document {document_id} not found")
        return document

    async def upload(self, workspace_id: UUID, file: UploadFile) -> Document:
        self._ensure_workspace(workspace_id)

        raw = await file.read()
        document_id = uuid4()
        filename = (file.filename or "upload.bin").strip() or "upload.bin"
        content_type = file.content_type or "application/octet-stream"
        lower_name = filename.lower()
        is_pdf = content_type == "application/pdf" or lower_name.endswith(".pdf")
        is_text = content_type.startswith("text/") or lower_name.endswith(_TEXT_SUFFIXES)

        if is_pdf:
            text_for_pii = extract_text_from_pdf(raw)
            safe_name = f"{PurePosixPath(filename).stem}.txt"
            stored_content_type = "text/plain"
        elif is_text:
            text_for_pii = raw.decode("utf-8", errors="ignore")
            safe_name = filename
            stored_content_type = content_type if content_type.startswith("text/") else "text/plain"
        else:
            raise ValidationAppError(
                "Formato não suportado. Envie .txt, .md, .csv ou .pdf com texto.",
            )

        storage_key = f"workspaces/{workspace_id}/safe/{document_id}/{safe_name}"

        document = self._repository.create(
            document_id=document_id,
            workspace_id=workspace_id,
            filename=filename,
            content_type=stored_content_type,
            size_bytes=0,
            storage_key=storage_key,
            status="processing",
        )

        pii_result = self._pii_service.anonymize_and_vault(
            text_for_pii,
            document_id=document.id,
        )
        payload = pii_result.text.encode("utf-8")

        self._storage.save(
            storage_key,
            payload,
            metadata={
                "workspace_id": str(workspace_id),
                "document_id": str(document.id),
                "filename": filename,
                "original_filename": filename,
            },
        )

        kb_sync_status = "skipped"
        kb_sync_job_id: str | None = None
        try:
            kb_sync_job_id = start_knowledge_base_sync()
            kb_sync_status = "started" if kb_sync_job_id else "skipped"
        except Exception:
            logger.exception("Knowledge Base sync failed after upload %s", document.id)
            kb_sync_status = "failed"

        document = self._repository.update_status(
            document.id,
            "ready",
            kb_sync_job_id=kb_sync_job_id,
            kb_sync_status=kb_sync_status,
            size_bytes=len(payload),
            storage_key=storage_key,
            content_type=stored_content_type,
        )

        self._audit.record_upload(
            workspace_id=workspace_id,
            document_id=document.id,
            pii_match_count=len(pii_result.matches),
            detail=f"filename={filename}; parsed_as={'pdf' if is_pdf else 'text'}",
        )
        self._audit.record_kb_sync(
            workspace_id=workspace_id,
            document_id=document.id,
            job_id=kb_sync_job_id,
            status=kb_sync_status,
        )
        return document

    def delete_document(self, workspace_id: UUID, document_id: UUID) -> None:
        document = self.get_document(workspace_id, document_id)
        self._storage.delete(document.storage_key)
        self._repository.delete(document)


def get_document_service(
    db: Annotated[Session, Depends(get_db)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    pii_service: Annotated[PiiService, Depends(get_pii_service)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
) -> DocumentService:
    return DocumentService(
        DocumentRepository(db),
        WorkspaceRepository(db),
        storage,
        pii_service,
        audit_service,
    )
