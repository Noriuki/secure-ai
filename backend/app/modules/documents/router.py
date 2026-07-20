from pathlib import PurePosixPath
from typing import Annotated
from urllib.parse import quote
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import Response

from app.modules.documents.schemas import DocumentResponse
from app.modules.documents.service import DocumentService, get_document_service
from app.shared.schemas import MessageResponse

router = APIRouter(
    prefix="/workspaces/{workspace_id}/documents",
    tags=["documents"],
)


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    workspace_id: UUID,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> list[DocumentResponse]:
    return service.list_documents(workspace_id)


@router.get("/{document_id}/content")
def open_document(
    workspace_id: UUID,
    document_id: UUID,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> Response:
    document, payload = service.read_document_content(workspace_id, document_id)
    filename = PurePosixPath(document.storage_key).name or document.filename
    ascii_name = filename.encode("ascii", "ignore").decode() or "document.txt"
    disposition = (
        f"inline; filename=\"{ascii_name}\"; "
        f"filename*=UTF-8''{quote(filename)}"
    )
    return Response(
        content=payload,
        media_type=document.content_type or "text/plain",
        headers={"Content-Disposition": disposition},
    )


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    workspace_id: UUID,
    document_id: UUID,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> DocumentResponse:
    return service.get_document(workspace_id, document_id)


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: UUID,
    service: Annotated[DocumentService, Depends(get_document_service)],
    file: Annotated[UploadFile, File()],
) -> DocumentResponse:
    return await service.upload(workspace_id, file)


@router.delete("/{document_id}", response_model=MessageResponse)
def delete_document(
    workspace_id: UUID,
    document_id: UUID,
    service: Annotated[DocumentService, Depends(get_document_service)],
) -> MessageResponse:
    service.delete_document(workspace_id, document_id)
    return MessageResponse(message="Document deleted")
