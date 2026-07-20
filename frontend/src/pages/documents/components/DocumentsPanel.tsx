import { useRef, useState, type DragEvent } from 'react'
import { documentContentUrl } from '../api'
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
  const [error, setError] = useState<string>()
  const [dragging, setDragging] = useState(false)

  async function handleFile(file: File | undefined) {
    if (!file) return
    setError(undefined)
    try {
      await upload(file)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha no upload. Tente outro arquivo.')
    }
  }

  function onDrop(event: DragEvent) {
    event.preventDefault()
    setDragging(false)
    void handleFile(event.dataTransfer.files?.[0])
  }

  async function onRemove(id: string, filename: string) {
    const ok = window.confirm(`Remover “${filename}” deste workspace?`)
    if (!ok) return
    try {
      await remove(id)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Não foi possível remover o documento')
    }
  }

  const count = state.status === 'ready' ? state.items.length : 0

  return (
    <section className="panel documents-panel">
      <div className="panel-head">
        <div>
          <h3>Documentos{count > 0 ? ` (${count})` : ''}</h3>
          <p className="muted small">
            Dados pessoais (CPF, e-mail, etc.) são anonimizados antes do armazenamento.
          </p>
        </div>
      </div>

      <div className="documents-body">
        {error && <p className="error">{error}</p>}
        {state.status === 'loading' && <p className="muted">Carregando documentos…</p>}
        {state.status === 'error' && <p className="error">{state.message}</p>}

        {state.status === 'ready' && state.items.length === 0 && !uploading && (
          <div className="empty-state compact">
            <p className="muted">Ainda sem arquivos. Envie o primeiro para liberar o chat.</p>
          </div>
        )}

        {state.status === 'ready' && state.items.length > 0 && (
          <ul className="list compact">
            {state.items.map((doc) => (
              <li key={doc.id} className="list-item">
                <a
                  className="list-main"
                  href={documentContentUrl(workspaceId, doc.id)}
                  target="_blank"
                  rel="noreferrer"
                >
                  <p className="list-title">{doc.filename}</p>
                  <p className="muted small">{formatBytes(doc.size_bytes)}</p>
                </a>
                <button
                  type="button"
                  className="btn-icon danger"
                  aria-label={`Remover ${doc.filename}`}
                  title="Remover"
                  onClick={() => void onRemove(doc.id, doc.filename)}
                >
                  <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
                    <path
                      fill="currentColor"
                      d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9zm-1 12h12a1 1 0 0 0 1-1V8H5v12a1 1 0 0 0 1 1z"
                    />
                  </svg>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <button
        type="button"
        className={`dropzone${dragging ? ' is-dragging' : ''}`}
        disabled={uploading}
        onClick={() => inputRef.current?.click()}
        onDragEnter={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragOver={(e) => e.preventDefault()}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <svg className="dropzone-icon" viewBox="0 0 24 24" width="22" height="22" aria-hidden="true">
          <path
            fill="currentColor"
            d="M12 3a1 1 0 0 1 1 1v8.59l2.3-2.3a1 1 0 1 1 1.4 1.42l-4 4a1 1 0 0 1-1.4 0l-4-4a1 1 0 1 1 1.4-1.42L11 12.59V4a1 1 0 0 1 1-1zM5 18a1 1 0 0 1 1-1h12a1 1 0 1 1 0 2H6a1 1 0 0 1-1-1z"
          />
        </svg>
        <strong>{uploading ? 'Preparando documento…' : 'Solte um arquivo aqui ou clique para escolher'}</strong>
        <span className="muted small">
          {uploading
            ? 'O arquivo só aparece na lista quando estiver pronto para o chat'
            : 'Formatos: .txt, .md, .csv, .pdf'}
        </span>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.md,.csv,.pdf,text/*"
        hidden
        onChange={(event) => {
          void handleFile(event.target.files?.[0])
          event.target.value = ''
        }}
      />
    </section>
  )
}
