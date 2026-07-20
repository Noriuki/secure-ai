export type Document = {
  id: string
  workspace_id: string
  filename: string
  content_type: string
  size_bytes: number
  storage_key: string
  status: string
  kb_sync_job_id?: string | null
  kb_sync_status?: string | null
  created_at: string
  updated_at: string
}
