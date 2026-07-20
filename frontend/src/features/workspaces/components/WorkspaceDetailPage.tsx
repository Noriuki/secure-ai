import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getWorkspace } from '../api'
import type { Workspace } from '../types'
import { DocumentsPanel } from '@/features/documents/components/DocumentsPanel'
import { ChatPanel } from '@/features/conversations/components/ChatPanel'

export function WorkspaceDetailPage() {
  const { workspaceId = '' } = useParams()
  const [workspace, setWorkspace] = useState<Workspace | null>(null)
  const [error, setError] = useState<string>()

  useEffect(() => {
    let active = true
    getWorkspace(workspaceId)
      .then((data) => {
        if (active) setWorkspace(data)
      })
      .catch((err: unknown) => {
        if (active) {
          setError(err instanceof Error ? err.message : 'Workspace não encontrado')
        }
      })
    return () => {
      active = false
    }
  }, [workspaceId])

  if (error) {
    return (
      <section className="panel">
        <p className="error">{error}</p>
        <Link to="/">← Voltar</Link>
      </section>
    )
  }

  if (!workspace) {
    return (
      <section className="panel">
        <p className="muted">Carregando workspace…</p>
      </section>
    )
  }

  return (
    <div className="workspace-layout">
      <div className="panel-head inline">
        <div>
          <Link className="back" to="/">
            ← Workspaces
          </Link>
          <h2>{workspace.name}</h2>
          {workspace.description && <p className="muted">{workspace.description}</p>}
        </div>
      </div>

      <div className="workspace-grid">
        <DocumentsPanel workspaceId={workspace.id} />
        <ChatPanel workspaceId={workspace.id} />
      </div>
    </div>
  )
}
