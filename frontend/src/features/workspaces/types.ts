export type Workspace = {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
}

export type WorkspaceCreate = {
  name: string
  description?: string
}
