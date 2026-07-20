import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getWorkspace } from '../api'
import type { Workspace } from '../types'
import { DocumentsPanel } from '@/pages/documents/components/DocumentsPanel'
import { ChatPanel } from '@/pages/conversations/components/ChatPanel'

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
        <p className="empty-title">Não encontramos esse workspace</p>
        <p className="error">{error}</p>
        <Link className="back" to="/">
          ← Voltar para a lista
        </Link>
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
            ← Todos os workspaces
          </Link>
          <h2>{workspace.name}</h2>
          {workspace.description ? (
            <p className="muted">{workspace.description}</p>
          ) : (
            <p className="muted">Envie documentos à esquerda e pergunte no chat à direita.</p>
          )}
        </div>
      </div>

      <ol className="steps" aria-label="Como usar">
        <li>
          <strong>1.</strong> Envie um arquivo (.txt, .md, .csv ou .pdf)
        </li>
        <li>
          <strong>2.</strong> Aguarde o arquivo aparecer na lista
        </li>
        <li>
          <strong>3.</strong> Pergunte no chat sobre o conteúdo
        </li>
      </ol>

      <div className="workspace-grid">
        <DocumentsPanel workspaceId={workspace.id} />
        <ChatPanel workspaceId={workspace.id} />
      </div>
    </div>
  )
}
