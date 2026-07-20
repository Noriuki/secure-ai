export type Conversation = {
  id: string
  workspace_id: string
  title: string
  created_at: string
  updated_at: string
}

export type Message = {
  id: string
  conversation_id: string
  role: 'user' | 'assistant' | 'system' | string
  content: string
  sources: Record<string, unknown>[]
  created_at: string
}

export type ChatResponse = {
  user_message: Message
  assistant_message: Message
}
