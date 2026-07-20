import { apiRequest } from '@/shared/api/client'
import type { Dashboard } from './types'

export function getDashboard() {
  return apiRequest<Dashboard>('/dashboard')
}
