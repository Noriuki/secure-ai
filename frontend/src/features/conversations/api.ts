import { apiRequest } from '@/shared/api/client'
import type { ChatResponse, Conversation, Message } from './types'

export function listConversations(workspaceId: string): Promise<Conversation[]> {
  return apiRequest<Conversation[]>(`/workspaces/${workspaceId}/conversations`)
}

export function createConversation(
  workspaceId: string,
  title = 'Nova conversa',
): Promise<Conversation> {
  return apiRequest<Conversation>(`/workspaces/${workspaceId}/conversations`, {
    method: 'POST',
    body: { title },
  })
}

export function listMessages(workspaceId: string, conversationId: string): Promise<Message[]> {
  return apiRequest<Message[]>(
    `/workspaces/${workspaceId}/conversations/${conversationId}/messages`,
  )
}

export function sendMessage(
  workspaceId: string,
  conversationId: string,
  content: string,
): Promise<ChatResponse> {
  return apiRequest<ChatResponse>(
    `/workspaces/${workspaceId}/conversations/${conversationId}/messages`,
    { method: 'POST', body: { content } },
  )
}
