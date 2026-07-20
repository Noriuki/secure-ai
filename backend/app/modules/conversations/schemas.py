from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas import OrmModel, TimestampMixin


class ConversationCreate(BaseModel):
    title: str = Field(default="Nova conversa", min_length=1, max_length=200)


class ConversationResponse(OrmModel, TimestampMixin):
    id: UUID
    workspace_id: UUID
    title: str


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(OrmModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sources: list[dict] = Field(default_factory=list)
    created_at: datetime


class ChatResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
