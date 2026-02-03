import { useSessions } from '../store'
import './SessionsList.css'

interface SessionsListProps {
  onSelectSession?: (sessionId: string) => void
}

export function SessionsList({ onSelectSession }: SessionsListProps) {
  const sessions = useSessions()

  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleDateString()
  }

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="sessions-list">
      {sessions.length === 0 ? (
        <div className="sessions-list__empty">No sessions yet</div>
      ) : (
        <div className="sessions-list__items">
          {sessions.map((session) => (
            <button
              key={session.id}
              className="sessions-list__item"
              onClick={() => onSelectSession?.(session.id)}
              data-testid={`session-${session.id}`}
            >
              <div className="sessions-list__item-title">{session.title}</div>
              <div className="sessions-list__item-meta">
                <span className="sessions-list__item-date">{formatDate(session.time_created)}</span>
                <span className="sessions-list__item-time">{formatTime(session.time_created)}</span>
                <span className="sessions-list__item-messages">{session.message_count} messages</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
