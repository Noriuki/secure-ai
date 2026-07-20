import { Link, Navigate, Route, Routes } from 'react-router-dom'
import { useHealth } from '@/features/health/hooks/useHealth'
import { WorkspaceListPage } from '@/features/workspaces/components/WorkspaceListPage'
import { WorkspaceDetailPage } from '@/features/workspaces/components/WorkspaceDetailPage'
import { DashboardPage } from '@/features/dashboard/components/DashboardPage'

export function App() {
  const health = useHealth()

  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="eyebrow">Secure AI</span>
          <strong>Workspace seguro</strong>
        </Link>
        <nav className="top-nav">
          <Link to="/">Workspaces</Link>
          <Link to="/dashboard">Observabilidade</Link>
          <p className="status" data-state={health.status}>
            {health.status === 'loading' && 'API…'}
            {health.status === 'ready' && `API ${health.data.status}`}
            {health.status === 'error' && `API offline`}
          </p>
        </nav>
      </header>

      <main className="page">
        <Routes>
          <Route path="/" element={<WorkspaceListPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/workspaces/:workspaceId" element={<WorkspaceDetailPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}
