import { useCallback, useEffect, useState } from 'react'
import { createWorkspace, deleteWorkspace, listWorkspaces } from '../api'
import type { Workspace, WorkspaceCreate } from '../types'

type State =
  | { status: 'loading' }
  | { status: 'ready'; items: Workspace[] }
  | { status: 'error'; message: string }

export function useWorkspaces() {
  const [state, setState] = useState<State>({ status: 'loading' })

  const refresh = useCallback(async () => {
    setState({ status: 'loading' })
    try {
      const items = await listWorkspaces()
      setState({ status: 'ready', items })
    } catch (error: unknown) {
      setState({
        status: 'error',
        message: error instanceof Error ? error.message : 'Falha ao carregar workspaces',
      })
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const add = useCallback(
    async (payload: WorkspaceCreate) => {
      const created = await createWorkspace(payload)
      setState((prev) =>
        prev.status === 'ready'
          ? { status: 'ready', items: [...prev.items, created] }
          : { status: 'ready', items: [created] },
      )
      return created
    },
    [],
  )

  const remove = useCallback(async (id: string) => {
    await deleteWorkspace(id)
    setState((prev) =>
      prev.status === 'ready'
        ? { status: 'ready', items: prev.items.filter((item) => item.id !== id) }
        : prev,
    )
  }, [])

  return { state, refresh, add, remove }
}
