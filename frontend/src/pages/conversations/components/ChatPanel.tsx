import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
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
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [state, sending])

  async function onSubmit(event?: FormEvent) {
    event?.preventDefault()
    const content = draft.trim()
    if (!content || sending) return
    setDraft('')
    setError(undefined)
    try {
      await send(content)
      inputRef.current?.focus()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Não foi possível enviar. Tente de novo.')
      setDraft(content)
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void onSubmit()
    }
  }

  return (
    <section className="panel chat-panel">
      <div className="panel-head">
        <div>
          <h3>Chat</h3>
          <p className="muted small">Pergunte sobre os documentos deste workspace.</p>
        </div>
      </div>

      {state.status === 'loading' && <p className="muted">Preparando conversa…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}

      {state.status === 'ready' && (
        <>
          <div className="chat-thread">
            {state.messages.length === 0 && !sending && (
              <div className="empty-state compact">
                <p className="empty-title">Comece a conversa</p>
                <p className="muted">
                  Ex.: “Resuma o contrato” ou “Quais são as obrigações das partes?”
                </p>
              </div>
            )}
            {state.messages.map((message) => {
              const titles = message.role === 'assistant' ? sourceTitles(message) : []
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
            {sending && (
              <article className="bubble" data-role="assistant">
                <p className="bubble-role">Assistente</p>
                <p className="typing">Pensando…</p>
              </article>
            )}
            <div ref={bottomRef} />
          </div>

          <form className="chat-compose" onSubmit={(e) => void onSubmit(e)}>
            <textarea
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={onKeyDown}
              placeholder="envia sua pergunta"
              disabled={sending}
              rows={1}
            />
            <button type="submit" disabled={sending || !draft.trim()}>
              {sending ? 'Enviando…' : 'Enviar'}
            </button>
          </form>
          {error && <p className="error">{error}</p>}
        </>
      )}
    </section>
  )
}
