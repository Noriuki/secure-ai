from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ValidationAppError
from app.modules.workspaces.models import Workspace
from app.modules.workspaces.schemas import WorkspaceCreate, WorkspaceUpdate
from app.shared.schemas import TimestampMixin


class WorkspaceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list(self) -> list[Workspace]:
        return list(self._db.scalars(select(Workspace).order_by(Workspace.created_at)).all())

    def get(self, workspace_id: UUID) -> Workspace | None:
        return self._db.get(Workspace, workspace_id)

    def create(self, data: WorkspaceCreate) -> Workspace:
        now = TimestampMixin.utcnow()
        workspace = Workspace(
            name=data.name.strip(),
            description=data.description.strip(),
            created_at=now,
            updated_at=now,
        )
        self._db.add(workspace)
        self._db.commit()
        self._db.refresh(workspace)
        return workspace

    def update(self, workspace_id: UUID, data: WorkspaceUpdate) -> Workspace:
        workspace = self.get(workspace_id)
        if workspace is None:
            raise NotFoundError(f"Workspace {workspace_id} not found")

        payload = data.model_dump(exclude_unset=True)
        if not payload:
            raise ValidationAppError("No fields to update")

        for field, value in payload.items():
            setattr(workspace, field, value if not isinstance(value, str) else value.strip())
        workspace.updated_at = TimestampMixin.utcnow()

        self._db.commit()
        self._db.refresh(workspace)
        return workspace

    def delete(self, workspace_id: UUID) -> None:
        workspace = self.get(workspace_id)
        if workspace is None:
            raise NotFoundError(f"Workspace {workspace_id} not found")
        self._db.delete(workspace)
        self._db.commit()
