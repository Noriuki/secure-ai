import { useCallback, useEffect, useState } from 'react'
import {
  createConversation,
  listConversations,
  listMessages,
  sendMessage,
} from '../api'
import type { Conversation, Message } from '../types'

type State =
  | { status: 'loading' }
  | { status: 'ready'; conversation: Conversation; messages: Message[] }
  | { status: 'error'; message: string }

export function useChat(workspaceId: string) {
  const [state, setState] = useState<State>({ status: 'loading' })
  const [sending, setSending] = useState(false)

  const bootstrap = useCallback(async () => {
    setState({ status: 'loading' })
    try {
      let conversations = await listConversations(workspaceId)
      if (conversations.length === 0) {
        const created = await createConversation(workspaceId)
        conversations = [created]
      }
      const conversation = conversations[0]
      const messages = await listMessages(workspaceId, conversation.id)
      setState({ status: 'ready', conversation, messages })
    } catch (error: unknown) {
      setState({
        status: 'error',
        message: error instanceof Error ? error.message : 'Falha ao iniciar chat',
      })
    }
  }, [workspaceId])

  useEffect(() => {
    void bootstrap()
  }, [bootstrap])

  const send = useCallback(
    async (content: string) => {
      if (state.status !== 'ready') return
      setSending(true)
      try {
        const result = await sendMessage(workspaceId, state.conversation.id, content)
        setState({
          status: 'ready',
          conversation: state.conversation,
          messages: [...state.messages, result.user_message, result.assistant_message],
        })
      } finally {
        setSending(false)
      }
    },
    [state, workspaceId],
  )

  return { state, sending, send, refresh: bootstrap }
}
