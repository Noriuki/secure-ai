import { useCallback, useEffect, useState } from 'react'
import { deleteDocument, listDocuments, uploadDocument } from '../api'
import type { Document } from '../types'

type State =
  | { status: 'loading' }
  | { status: 'ready'; items: Document[] }
  | { status: 'error'; message: string }

export function useDocuments(workspaceId: string) {
  const [state, setState] = useState<State>({ status: 'loading' })
  const [uploading, setUploading] = useState(false)

  const refresh = useCallback(async () => {
    setState({ status: 'loading' })
    try {
      const items = await listDocuments(workspaceId)
      setState({ status: 'ready', items })
    } catch (error: unknown) {
      setState({
        status: 'error',
        message: error instanceof Error ? error.message : 'Falha ao carregar documentos',
      })
    }
  }, [workspaceId])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const upload = useCallback(
    async (file: File) => {
      setUploading(true)
      try {
        const created = await uploadDocument(workspaceId, file)
        setState((prev) =>
          prev.status === 'ready'
            ? { status: 'ready', items: [created, ...prev.items] }
            : { status: 'ready', items: [created] },
        )
        return created
      } finally {
        setUploading(false)
      }
    },
    [workspaceId],
  )

  const remove = useCallback(
    async (documentId: string) => {
      await deleteDocument(workspaceId, documentId)
      setState((prev) =>
        prev.status === 'ready'
          ? { status: 'ready', items: prev.items.filter((item) => item.id !== documentId) }
          : prev,
      )
    },
    [workspaceId],
  )

  return { state, uploading, refresh, upload, remove }
}
