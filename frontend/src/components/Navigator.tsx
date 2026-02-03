import { useState } from 'react'
import './Navigator.css'

interface NavigatorProps {
  onJump: (messageId: string) => void
}

interface NavigatorItem {
  id: string
  role: string
  title: string
  timestamp: number
}

export function Navigator({ onJump }: NavigatorProps) {
  const [navigatorItems] = useState<NavigatorItem[]>([
    { id: 'm1', role: 'user', title: 'Initialize project setup', timestamp: Date.now() - 300000 },
    { id: 'm2', role: 'agent', title: 'Planned implementation steps', timestamp: Date.now() - 290000 },
    { id: 'm3', role: 'tool', title: 'grep: searched for dependencies', timestamp: Date.now() - 280000 },
    { id: 'm4', role: 'agent', title: 'Created base components', timestamp: Date.now() - 270000 },
    { id: 'm5', role: 'user', title: 'Review changes', timestamp: Date.now() - 260000 },
  ])

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'user':
        return 'var(--accent-primary)'
      case 'agent':
        return 'var(--success)'
      case 'tool':
        return 'var(--warning)'
      default:
        return 'var(--text-secondary)'
    }
  }

  return (
    <div className="navigator">
      {navigatorItems.length === 0 ? (
        <div className="navigator__empty">No messages to navigate</div>
      ) : (
        <div className="navigator__items">
          {navigatorItems.map((item) => (
            <button
              key={item.id}
              className="navigator__item"
              onClick={() => onJump(item.id)}
              data-testid={`navigator-${item.id}`}
            >
              <div
                className="navigator__item-role"
                style={{ color: getRoleColor(item.role) }}
              >
                {item.role.toUpperCase()}
              </div>
              <div className="navigator__item-title">{item.title}</div>
              <div className="navigator__item-time">{formatTime(item.timestamp)}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
