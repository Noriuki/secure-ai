import asyncio
import logging
from pathlib import PurePosixPath
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import Depends, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import NotFoundError, ValidationAppError
from app.integrations.bedrock.sync import sync_knowledge_base
from app.integrations.pii.protocols import PiiProcessor
from app.integrations.pii.provider import get_pii_processor
from app.integrations.storage.protocols import StoragePort
from app.integrations.storage.provider import get_storage
from app.modules.documents.models import Document
from app.modules.documents.pii import anonymize_text, save_vault_matches
from app.modules.documents.repository import DocumentRepository
from app.modules.workspaces.repository import WorkspaceRepository
from app.shared.parsing.pdf import extract_text_from_pdf

logger = logging.getLogger(__name__)

_TEXT_SUFFIXES = (".txt", ".md", ".csv")


class DocumentService:
    def __init__(
        self,
        db: Session,
        repository: DocumentRepository,
        workspace_repository: WorkspaceRepository,
        storage: StoragePort,
        pii_processor: PiiProcessor,
    ) -> None:
        self._db = db
        self._repository = repository
        self._workspace_repository = workspace_repository
        self._storage = storage
        self._pii_processor = pii_processor

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
        pii_result = anonymize_text(
            self._pii_processor,
            text_for_pii,
            document_id=document_id,
        )
        payload = pii_result.text.encode("utf-8")

        self._storage.save(
            storage_key,
            payload,
            metadata={
                "workspace_id": str(workspace_id),
                "document_id": str(document_id),
                "filename": filename,
                "original_filename": filename,
            },
        )

        try:
            sync_result = await asyncio.to_thread(sync_knowledge_base)
        except Exception:
            logger.exception("Knowledge Base sync failed for upload %s", document_id)
            self._storage.delete(storage_key)
            raise ValidationAppError(
                "Falha ao indexar o documento na Knowledge Base. Tente novamente.",
            ) from None

        if sync_result.status not in {"complete", "skipped"}:
            self._storage.delete(storage_key)
            raise ValidationAppError(
                "A indexação na Knowledge Base não concluiu a tempo. Tente novamente.",
            )

        document = self._repository.create(
            document_id=document_id,
            workspace_id=workspace_id,
            filename=filename,
            content_type=stored_content_type,
            size_bytes=len(payload),
            storage_key=storage_key,
            status="ready",
            kb_sync_job_id=sync_result.job_id,
            kb_sync_status=sync_result.status,
        )
        save_vault_matches(self._db, document.id, pii_result.matches)
        return document

    def delete_document(self, workspace_id: UUID, document_id: UUID) -> None:
        document = self.get_document(workspace_id, document_id)
        self._storage.delete(document.storage_key)
        self._repository.delete(document)

    def read_document_content(
        self,
        workspace_id: UUID,
        document_id: UUID,
    ) -> tuple[Document, bytes]:
        document = self.get_document(workspace_id, document_id)
        try:
            payload = self._storage.read(document.storage_key)
        except FileNotFoundError as exc:
            raise NotFoundError(f"Content for document {document_id} not found") from exc
        return document, payload


def get_document_service(
    db: Annotated[Session, Depends(get_db)],
    storage: Annotated[StoragePort, Depends(get_storage)],
    pii_processor: Annotated[PiiProcessor, Depends(get_pii_processor)],
) -> DocumentService:
    return DocumentService(
        db,
        DocumentRepository(db),
        WorkspaceRepository(db),
        storage,
        pii_processor,
    )
