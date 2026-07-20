from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.workspaces.schemas import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from app.modules.workspaces.service import WorkspaceService, get_workspace_service
from app.shared.schemas import MessageResponse

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> list[WorkspaceResponse]:
    return service.list_workspaces()


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    return service.get_workspace(workspace_id)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    payload: WorkspaceCreate,
    service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    return service.create_workspace(payload)


@router.patch("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> WorkspaceResponse:
    return service.update_workspace(workspace_id, payload)


@router.delete("/{workspace_id}", response_model=MessageResponse)
def delete_workspace(
    workspace_id: UUID,
    service: Annotated[WorkspaceService, Depends(get_workspace_service)],
) -> MessageResponse:
    service.delete_workspace(workspace_id)
    return MessageResponse(message="Workspace deleted")
