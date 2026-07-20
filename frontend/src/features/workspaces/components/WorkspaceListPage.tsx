import { useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { useWorkspaces } from '../hooks/useWorkspaces'

export function WorkspaceListPage() {
  const { state, add, remove } = useWorkspaces()
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    if (!name.trim()) return
    setBusy(true)
    setError(undefined)
    try {
      await add({ name: name.trim(), description: description.trim() })
      setName('')
      setDescription('')
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Falha ao criar workspace')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>Workspaces</h2>
          <p className="muted">Organize documentos e conversas por contexto.</p>
        </div>
      </div>

      <form className="form-row" onSubmit={onSubmit}>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nome do workspace"
          maxLength={120}
          required
        />
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Descrição (opcional)"
        />
        <button type="submit" disabled={busy}>
          {busy ? 'Criando…' : 'Criar'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {state.status === 'loading' && <p className="muted">Carregando…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}
      {state.status === 'ready' && state.items.length === 0 && (
        <p className="muted">Nenhum workspace ainda. Crie o primeiro acima.</p>
      )}

      {state.status === 'ready' && state.items.length > 0 && (
        <ul className="list">
          {state.items.map((workspace) => (
            <li key={workspace.id} className="list-item">
              <div>
                <Link className="list-title" to={`/workspaces/${workspace.id}`}>
                  {workspace.name}
                </Link>
                {workspace.description && <p className="muted small">{workspace.description}</p>}
              </div>
              <button
                type="button"
                className="btn-ghost danger"
                onClick={() => void remove(workspace.id)}
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
