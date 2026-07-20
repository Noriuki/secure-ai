from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.modules.conversations.schemas import (
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.modules.conversations.service import ConversationService, get_conversation_service
from app.shared.schemas import MessageResponse as ApiMessageResponse

router = APIRouter(
    prefix="/workspaces/{workspace_id}/conversations",
    tags=["conversations"],
)


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    workspace_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> list[ConversationResponse]:
    return service.list_conversations(workspace_id)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    workspace_id: UUID,
    payload: ConversationCreate,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> ConversationResponse:
    return service.create_conversation(workspace_id, payload)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    workspace_id: UUID,
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> ConversationResponse:
    return service.get_conversation(workspace_id, conversation_id)


@router.delete("/{conversation_id}", response_model=ApiMessageResponse)
def delete_conversation(
    workspace_id: UUID,
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> ApiMessageResponse:
    service.delete_conversation(workspace_id, conversation_id)
    return ApiMessageResponse(message="Conversation deleted")


@router.get("/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(
    workspace_id: UUID,
    conversation_id: UUID,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> list[MessageResponse]:
    return service.list_messages(workspace_id, conversation_id)


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    workspace_id: UUID,
    conversation_id: UUID,
    payload: MessageCreate,
    service: Annotated[ConversationService, Depends(get_conversation_service)],
) -> ChatResponse:
    return service.send_message(workspace_id, conversation_id, payload)
