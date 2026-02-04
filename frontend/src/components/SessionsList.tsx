import { useSessions } from '../store'

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
    <div>
      {sessions.length === 0 ? (
        <div className="text-tertiary font-mono text-sm text-center p-3 opacity-70">No sessions yet</div>
      ) : (
        <div className="flex flex-col gap-2">
          {sessions.map((session) => (
            <button
              key={session.id}
              className="bg-surface-raised border border-normal rounded-[14px] text-primary cursor-pointer font-mono p-3 text-left transition-all duration-150 w-full hover:bg-surface-base hover:border-focus focus-visible:outline-2 focus-visible:outline-accent-primary focus-visible:outline-offset-2"
              onClick={() => onSelectSession?.(session.id)}
              data-testid={`session-${session.id}`}
            >
              <div className="text-sm font-medium mb-2 overflow-hidden text-ellipsis whitespace-nowrap">{session.title}</div>
              <div className="flex items-center gap-3 text-secondary text-xs">
                <span className="opacity-80">{formatDate(session.time_created)}</span>
                <span className="opacity-80">{formatTime(session.time_created)}</span>
                <span className="opacity-80">{session.message_count} messages</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
