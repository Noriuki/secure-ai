export type AuditEvent = {
  id: string
  workspace_id: string | null
  conversation_id: string | null
  document_id: string | null
  message_id: string | null
  event_type: string
  model: string | null
  latency_ms: number | null
  pii_match_count: number
  source_count: number
  estimated_cost_usd: number | null
  detail: string | null
  created_at: string
}

export type Dashboard = {
  workspaces: number
  documents: number
  conversations: number
  messages: number
  llm_calls: number
  avg_latency_ms: number | null
  pii_detections: number
  estimated_cost_usd: number
  recent_events: AuditEvent[]
}
