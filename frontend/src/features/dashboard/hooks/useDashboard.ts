import { useEffect, useState } from 'react'
import { getDashboard } from '../api'
import type { Dashboard } from '../types'

type State =
  | { status: 'loading' }
  | { status: 'ready'; data: Dashboard }
  | { status: 'error'; message: string }

export function useDashboard() {
  const [state, setState] = useState<State>({ status: 'loading' })

  useEffect(() => {
    let active = true
    getDashboard()
      .then((data) => {
        if (active) setState({ status: 'ready', data })
      })
      .catch((err: unknown) => {
        if (active) {
          setState({
            status: 'error',
            message: err instanceof Error ? err.message : 'Falha ao carregar dashboard',
          })
        }
      })
    return () => {
      active = false
    }
  }, [])

  return state
}
