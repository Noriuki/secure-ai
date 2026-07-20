import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useChat } from '../hooks/useChat'
import type { Message } from '../types'

type Props = {
  workspaceId: string
}

function sourceTitles(message: Message): string[] {
  const titles: string[] = []
  const seen = new Set<string>()
  for (const source of message.sources) {
    const title = String(source.title ?? '').trim()
    if (!title || seen.has(title)) continue
    seen.add(title)
    titles.push(title)
  }
  return titles
}

export function ChatPanel({ workspaceId }: Props) {
  const { state, sending, send } = useChat(workspaceId)
  const [draft, setDraft] = useState('')
  const [error, setError] = useState<string>()
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state])

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    const content = draft.trim()
    if (!content || sending) return
    setDraft('')
    setError(undefined)
    try {
      await send(content)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao enviar mensagem')
      setDraft(content)
    }
  }

  return (
    <section className="panel chat-panel">
      <div className="panel-head">
        <div>
          <h3>Chat</h3>
          <p className="muted small">Respostas via Bedrock Knowledge Base.</p>
        </div>
      </div>

      {state.status === 'loading' && <p className="muted">Preparando conversa…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}

      {state.status === 'ready' && (
        <>
          <div className="chat-thread">
            {state.messages.length === 0 && (
              <p className="muted">Pergunte algo sobre os documentos deste workspace.</p>
            )}
            {state.messages.map((message) => {
              const titles =
                message.role === 'assistant' ? sourceTitles(message) : []
              return (
                <article
                  key={message.id}
                  className="bubble"
                  data-role={message.role === 'user' ? 'user' : 'assistant'}
                >
                  <p className="bubble-role">
                    {message.role === 'user' ? 'Você' : 'Assistente'}
                  </p>
                  <p>{message.content}</p>
                  {titles.length > 0 && (
                    <p className="bubble-sources">Fontes: {titles.join(' · ')}</p>
                  )}
                </article>
              )
            })}
            <div ref={bottomRef} />
          </div>

          <form className="chat-compose" onSubmit={onSubmit}>
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Digite sua pergunta…"
              disabled={sending}
            />
            <button type="submit" disabled={sending || !draft.trim()}>
              {sending ? '…' : 'Enviar'}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
        </>
      )}
    </section>
  )
}
