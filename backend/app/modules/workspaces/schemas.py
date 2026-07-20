from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas import OrmModel, TimestampMixin


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None


class WorkspaceResponse(OrmModel, TimestampMixin):
    id: UUID
    name: str
    description: str
