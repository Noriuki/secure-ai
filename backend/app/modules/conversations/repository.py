import json
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.modules.conversations.models import Conversation, Message
from app.modules.conversations.schemas import ConversationCreate
from app.shared.schemas import TimestampMixin


class ConversationRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_by_workspace(self, workspace_id: UUID) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.workspace_id == workspace_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(self._db.scalars(stmt).all())

    def get(self, conversation_id: UUID) -> Conversation | None:
        return self._db.get(Conversation, conversation_id)

    def get_in_workspace(self, workspace_id: UUID, conversation_id: UUID) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.workspace_id == workspace_id,
        )
        return self._db.scalars(stmt).first()

    def create(self, workspace_id: UUID, data: ConversationCreate) -> Conversation:
        now = TimestampMixin.utcnow()
        conversation = Conversation(
            workspace_id=workspace_id,
            title=data.title.strip(),
            created_at=now,
            updated_at=now,
        )
        self._db.add(conversation)
        self._db.commit()
        self._db.refresh(conversation)
        return conversation

    def touch(self, conversation: Conversation) -> None:
        conversation.updated_at = TimestampMixin.utcnow()
        self._db.commit()

    def delete(self, conversation: Conversation) -> None:
        self._db.delete(conversation)
        self._db.commit()

    def list_messages(self, conversation_id: UUID) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(self._db.scalars(stmt).all())

    def add_message(
        self,
        *,
        conversation_id: UUID,
        role: str,
        content: str,
        sources: list[dict] | None = None,
    ) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources_json=json.dumps(sources or []),
            created_at=TimestampMixin.utcnow(),
        )
        self._db.add(message)
        self._db.commit()
        self._db.refresh(message)
        return message

    def get_conversation_or_raise(self, conversation_id: UUID) -> Conversation:
        conversation = self.get(conversation_id)
        if conversation is None:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        return conversation
