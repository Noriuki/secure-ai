import { apiRequest, apiUpload } from "@/services/api/client";
import type { Document } from "./types";

export function listDocuments(workspaceId: string): Promise<Document[]> {
  return apiRequest<Document[]>(`/workspaces/${workspaceId}/documents`);
}

export function uploadDocument(
  workspaceId: string,
  file: File,
): Promise<Document> {
  return apiUpload<Document>(`/workspaces/${workspaceId}/documents`, file);
}

export function deleteDocument(
  workspaceId: string,
  documentId: string,
): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(
    `/workspaces/${workspaceId}/documents/${documentId}`,
    { method: "DELETE" },
  );
}

export function documentContentUrl(
  workspaceId: string,
  documentId: string,
): string {
  const base = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
  return `${base}/workspaces/${workspaceId}/documents/${documentId}/content`;
}
