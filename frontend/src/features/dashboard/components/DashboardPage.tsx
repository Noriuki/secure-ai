import { Link } from 'react-router-dom'
import { useDashboard } from '../hooks/useDashboard'

function formatCost(value: number): string {
  return `$${value.toFixed(4)}`
}

function formatWhen(iso: string): string {
  try {
    return new Date(iso).toLocaleString('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    })
  } catch {
    return iso
  }
}

export function DashboardPage() {
  const state = useDashboard()

  return (
    <section className="panel">
      <div className="panel-head inline">
        <div>
          <Link className="back" to="/">
            ← Workspaces
          </Link>
          <h2>Observabilidade</h2>
          <p className="muted">Auditoria de uploads, chat e sync da Knowledge Base.</p>
        </div>
      </div>

      {state.status === 'loading' && <p className="muted">Carregando métricas…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}

      {state.status === 'ready' && (
        <>
          <div className="stats-grid">
            <div className="stat">
              <span className="stat-label">Workspaces</span>
              <strong>{state.data.workspaces}</strong>
            </div>
            <div className="stat">
              <span className="stat-label">Documentos</span>
              <strong>{state.data.documents}</strong>
            </div>
            <div className="stat">
              <span className="stat-label">Chamadas LLM</span>
              <strong>{state.data.llm_calls}</strong>
            </div>
            <div className="stat">
              <span className="stat-label">Latência média</span>
              <strong>
                {state.data.avg_latency_ms != null
                  ? `${state.data.avg_latency_ms} ms`
                  : '—'}
              </strong>
            </div>
            <div className="stat">
              <span className="stat-label">PII detectado</span>
              <strong>{state.data.pii_detections}</strong>
            </div>
            <div className="stat">
              <span className="stat-label">Custo estimado</span>
              <strong>{formatCost(state.data.estimated_cost_usd)}</strong>
            </div>
          </div>

          <h3 className="section-title">Eventos recentes</h3>
          {state.data.recent_events.length === 0 ? (
            <p className="muted">Nenhum evento ainda.</p>
          ) : (
            <ul className="list compact">
              {state.data.recent_events.map((event) => (
                <li key={event.id} className="list-item">
                  <div>
                    <p className="list-title">{event.event_type}</p>
                    <p className="muted small">
                      {formatWhen(event.created_at)}
                      {event.model ? ` · ${event.model}` : ''}
                      {event.latency_ms != null ? ` · ${event.latency_ms} ms` : ''}
                      {event.pii_match_count
                        ? ` · ${event.pii_match_count} PII`
                        : ''}
                      {event.estimated_cost_usd != null
                        ? ` · ${formatCost(event.estimated_cost_usd)}`
                        : ''}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </section>
  )
}
