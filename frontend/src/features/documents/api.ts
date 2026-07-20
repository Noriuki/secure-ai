import { apiRequest, apiUpload } from '@/shared/api/client'
import type { Document } from './types'

export function listDocuments(workspaceId: string): Promise<Document[]> {
  return apiRequest<Document[]>(`/workspaces/${workspaceId}/documents`)
}

export function uploadDocument(workspaceId: string, file: File): Promise<Document> {
  return apiUpload<Document>(`/workspaces/${workspaceId}/documents`, file)
}

export function deleteDocument(workspaceId: string, documentId: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(
    `/workspaces/${workspaceId}/documents/${documentId}`,
    { method: 'DELETE' },
  )
}
