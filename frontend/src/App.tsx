import { Link, Navigate, Route, Routes } from 'react-router-dom'
import { WorkspaceListPage } from '@/pages/workspaces/components/WorkspaceListPage'
import { WorkspaceDetailPage } from '@/pages/workspaces/components/WorkspaceDetailPage'

export function App() {
  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="eyebrow">Secure AI</span>
          <strong>Workspace seguro</strong>
        </Link>
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<WorkspaceListPage />} />
          <Route path="/workspaces/:workspaceId" element={<WorkspaceDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
