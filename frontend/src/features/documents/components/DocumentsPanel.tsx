import { useRef } from 'react'
import { useDocuments } from '../hooks/useDocuments'

type Props = {
  workspaceId: string
}

function formatBytes(size: number): string {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

export function DocumentsPanel({ workspaceId }: Props) {
  const { state, uploading, upload, remove } = useDocuments(workspaceId)
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h3>Documentos</h3>
          <p className="muted small">Upload para o workspace (S3 + Presidio PT).</p>
        </div>
        <button type="button" onClick={() => inputRef.current?.click()} disabled={uploading}>
          {uploading ? 'Enviando…' : 'Upload'}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".txt,.md,.csv,.pdf,text/*"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0]
            if (file) void upload(file)
            event.target.value = ''
          }}
        />
      </div>

      {state.status === 'loading' && <p className="muted">Carregando…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}
      {state.status === 'ready' && state.items.length === 0 && (
        <p className="muted">Nenhum documento enviado.</p>
      )}

      {state.status === 'ready' && state.items.length > 0 && (
        <ul className="list compact">
          {state.items.map((doc) => (
            <li key={doc.id} className="list-item">
              <div>
                <p className="list-title">{doc.filename}</p>
                <p className="muted small">
                  {doc.status}
                  {doc.kb_sync_status ? ` · kb ${doc.kb_sync_status}` : ''}
                  {' · '}
                  {formatBytes(doc.size_bytes)}
                </p>
              </div>
              <button
                type="button"
                className="btn-ghost danger"
                onClick={() => void remove(doc.id)}
              >
                Remover
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
