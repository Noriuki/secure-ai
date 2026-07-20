from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import NotFoundError
from app.modules.workspaces.models import Workspace
from app.modules.workspaces.repository import WorkspaceRepository
from app.modules.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    def __init__(self, repository: WorkspaceRepository) -> None:
        self._repository = repository

    def list_workspaces(self) -> list[Workspace]:
        return self._repository.list()

    def get_workspace(self, workspace_id: UUID) -> Workspace:
        workspace = self._repository.get(workspace_id)
        if workspace is None:
            raise NotFoundError(f"Workspace {workspace_id} not found")
        return workspace

    def create_workspace(self, data: WorkspaceCreate) -> Workspace:
        return self._repository.create(data)

    def update_workspace(self, workspace_id: UUID, data: WorkspaceUpdate) -> Workspace:
        return self._repository.update(workspace_id, data)

    def delete_workspace(self, workspace_id: UUID) -> None:
        self._repository.delete(workspace_id)


def get_workspace_service(db: Annotated[Session, Depends(get_db)]) -> WorkspaceService:
    return WorkspaceService(WorkspaceRepository(db))
