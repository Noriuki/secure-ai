import json
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.exceptions import NotFoundError
from app.core.security.service import PiiService, get_pii_service
from app.integrations.bedrock.protocols import RagPort
from app.integrations.bedrock.provider import get_rag
from app.modules.audit.service import AuditService, get_audit_service
from app.modules.conversations.models import Conversation, Message
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.schemas import (
    ChatResponse,
    ConversationCreate,
    MessageCreate,
    MessageResponse,
)
from app.modules.workspaces.repository import WorkspaceRepository


def message_to_response(message: Message) -> MessageResponse:
    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        sources=json.loads(message.sources_json or "[]"),
        created_at=message.created_at,
    )


class ConversationService:
    def __init__(
        self,
        repository: ConversationRepository,
        workspace_repository: WorkspaceRepository,
        pii_service: PiiService,
        rag: RagPort,
        audit_service: AuditService,
    ) -> None:
        self._repository = repository
        self._workspace_repository = workspace_repository
        self._pii_service = pii_service
        self._rag = rag
        self._audit = audit_service

    def _ensure_workspace(self, workspace_id: UUID) -> None:
        if self._workspace_repository.get(workspace_id) is None:
            raise NotFoundError(f"Workspace {workspace_id} not found")

    def list_conversations(self, workspace_id: UUID) -> list[Conversation]:
        self._ensure_workspace(workspace_id)
        return self._repository.list_by_workspace(workspace_id)

    def create_conversation(self, workspace_id: UUID, data: ConversationCreate) -> Conversation:
        self._ensure_workspace(workspace_id)
        return self._repository.create(workspace_id, data)

    def get_conversation(self, workspace_id: UUID, conversation_id: UUID) -> Conversation:
        self._ensure_workspace(workspace_id)
        conversation = self._repository.get_in_workspace(workspace_id, conversation_id)
        if conversation is None:
            raise NotFoundError(f"Conversation {conversation_id} not found")
        return conversation

    def delete_conversation(self, workspace_id: UUID, conversation_id: UUID) -> None:
        conversation = self.get_conversation(workspace_id, conversation_id)
        self._repository.delete(conversation)

    def list_messages(self, workspace_id: UUID, conversation_id: UUID) -> list[MessageResponse]:
        self.get_conversation(workspace_id, conversation_id)
        messages = self._repository.list_messages(conversation_id)
        return [message_to_response(message) for message in messages]

    def send_message(
        self,
        workspace_id: UUID,
        conversation_id: UUID,
        data: MessageCreate,
    ) -> ChatResponse:
        conversation = self.get_conversation(workspace_id, conversation_id)

        safe = self._pii_service.anonymize_and_vault(data.content.strip())
        user_message = self._repository.add_message(
            conversation_id=conversation.id,
            role="user",
            content=safe.text,
        )

        reply = self._rag.ask(workspace_id=workspace_id, question=safe.text)
        sources = [
            {
                "title": source.title,
                "excerpt": source.excerpt,
                "uri": source.uri,
                "score": source.score,
            }
            for source in reply.sources
        ]
        assistant_message = self._repository.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=reply.answer,
            sources=sources,
        )
        self._repository.touch(conversation)

        self._audit.record_chat(
            workspace_id=workspace_id,
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            model=reply.model,
            latency_ms=reply.latency_ms,
            pii_match_count=len(safe.matches),
            source_count=len(sources),
        )

        return ChatResponse(
            user_message=message_to_response(user_message),
            assistant_message=message_to_response(assistant_message),
        )


def get_conversation_service(
    db: Annotated[Session, Depends(get_db)],
    pii_service: Annotated[PiiService, Depends(get_pii_service)],
    rag: Annotated[RagPort, Depends(get_rag)],
    audit_service: Annotated[AuditService, Depends(get_audit_service)],
) -> ConversationService:
    return ConversationService(
        ConversationRepository(db),
        WorkspaceRepository(db),
        pii_service,
        rag,
        audit_service,
    )
