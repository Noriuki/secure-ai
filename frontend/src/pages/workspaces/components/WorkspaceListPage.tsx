import { useEffect, useId, useRef, useState, type FormEvent } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { useWorkspaces } from '../hooks/useWorkspaces'

export function WorkspaceListPage() {
  const { state, add, remove } = useWorkspaces()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()
  const [listError, setListError] = useState<string>()
  const nameRef = useRef<HTMLInputElement>(null)
  const titleId = useId()

  useEffect(() => {
    if (!open) return

    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    nameRef.current?.focus()

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape' && !busy) closeModal()
    }
    window.addEventListener('keydown', onKeyDown)
    return () => {
      document.body.style.overflow = previousOverflow
      window.removeEventListener('keydown', onKeyDown)
    }
  }, [open, busy])

  function closeModal() {
    setOpen(false)
    setName('')
    setDescription('')
    setError(undefined)
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim()) return
    setBusy(true)
    setError(undefined)
    try {
      await add({ name: name.trim(), description: description.trim() })
      closeModal()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Não foi possível criar o workspace')
    } finally {
      setBusy(false)
    }
  }

  async function onRemove(id: string, workspaceName: string) {
    const ok = window.confirm(
      `Remover “${workspaceName}”? Documentos e conversas desse workspace também serão apagados.`,
    )
    if (!ok) return
    try {
      await remove(id)
    } catch (err: unknown) {
      setListError(err instanceof Error ? err.message : 'Não foi possível remover')
    }
  }

  const modal =
    open &&
    createPortal(
      <div
        className="modal-backdrop"
        role="presentation"
        onClick={(event) => {
          if (event.target === event.currentTarget && !busy) closeModal()
        }}
      >
        <div className="modal" role="dialog" aria-modal="true" aria-labelledby={titleId}>
          <div className="modal-head">
            <h3 id={titleId}>Novo workspace</h3>
            <button
              type="button"
              className="btn-ghost"
              onClick={closeModal}
              disabled={busy}
              aria-label="Fechar"
            >
              Fechar
            </button>
          </div>

          <form className="form-stack modal-form" onSubmit={onSubmit}>
            <label className="field">
              <span>Nome</span>
              <input
                ref={nameRef}
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Ex.: Contratos 2024"
                maxLength={120}
                required
                autoComplete="off"
              />
            </label>
            <label className="field">
              <span>Descrição (opcional)</span>
              <input
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Para que serve este espaço"
                autoComplete="off"
              />
            </label>
            {error && <p className="error">{error}</p>}
            <div className="modal-actions">
              <button type="button" className="btn-ghost" onClick={closeModal} disabled={busy}>
                Cancelar
              </button>
              <button type="submit" disabled={busy || !name.trim()}>
                {busy ? 'Criando…' : 'Criar workspace'}
              </button>
            </div>
          </form>
        </div>
      </div>,
      document.body,
    )

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>Seus workspaces</h2>
        </div>
        <button type="button" onClick={() => setOpen(true)}>
          Novo workspace
        </button>
      </div>

      {listError && <p className="error">{listError}</p>}

      {state.status === 'loading' && <p className="muted">Carregando workspaces…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}

      {state.status === 'ready' && state.items.length === 0 && (
        <p className="muted">Nenhum workspace ainda.</p>
      )}

      {state.status === 'ready' && state.items.length > 0 && (
        <ul className="list">
          {state.items.map((workspace) => (
            <li key={workspace.id} className="list-item">
              <Link className="list-main" to={`/workspaces/${workspace.id}`}>
                <p className="list-title">{workspace.name}</p>
                {workspace.description ? (
                  <p className="muted small">{workspace.description}</p>
                ) : (
                  <p className="muted small">Abrir para enviar documentos e conversar</p>
                )}
              </Link>
              <button
                type="button"
                className="btn-icon danger"
                aria-label={`Remover ${workspace.name}`}
                title="Remover"
                onClick={() => void onRemove(workspace.id, workspace.name)}
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

      {modal}
    </section>
  )
}
