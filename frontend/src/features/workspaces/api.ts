import { apiRequest } from '@/shared/api/client'
import type { Workspace, WorkspaceCreate } from './types'

export function listWorkspaces(): Promise<Workspace[]> {
  return apiRequest<Workspace[]>('/workspaces')
}

export function getWorkspace(id: string): Promise<Workspace> {
  return apiRequest<Workspace>(`/workspaces/${id}`)
}

export function createWorkspace(payload: WorkspaceCreate): Promise<Workspace> {
  return apiRequest<Workspace>('/workspaces', { method: 'POST', body: payload })
}

export function deleteWorkspace(id: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(`/workspaces/${id}`, { method: 'DELETE' })
}
