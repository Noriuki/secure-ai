import { useEffect, useState } from 'react'
import { getHealth } from '../api'
import type { HealthStatus } from '../types'

type HealthState =
  | { status: 'loading' }
  | { status: 'ready'; data: HealthStatus }
  | { status: 'error'; message: string }

export function useHealth() {
  const [state, setState] = useState<HealthState>({ status: 'loading' })

  useEffect(() => {
    let active = true

    getHealth()
      .then((data) => {
        if (active) setState({ status: 'ready', data })
      })
      .catch((error: unknown) => {
        if (active) {
          setState({
            status: 'error',
            message: error instanceof Error ? error.message : 'Failed to reach API',
          })
        }
      })

    return () => {
      active = false
    }
  }, [])

  return state
}
