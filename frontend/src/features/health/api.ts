import { apiRequest } from '@/shared/api/client'
import type { HealthStatus } from './types'

export function getHealth(): Promise<HealthStatus> {
  return apiRequest<HealthStatus>('/health')
}
