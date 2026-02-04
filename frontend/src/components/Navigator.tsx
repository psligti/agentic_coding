import { useState } from 'react'

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
        return 'text-accent-primary'
      case 'agent':
        return 'text-success'
      case 'tool':
        return 'text-warning'
      default:
        return 'text-secondary'
    }
  }

  return (
    <div>
      {navigatorItems.length === 0 ? (
        <div className="text-tertiary font-mono text-sm text-center p-3 opacity-70">
          No messages to navigate
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {navigatorItems.map((item) => (
            <button
              key={item.id}
              className="bg-surface-raised border border-normal rounded-[14px] cursor-pointer font-mono p-3 text-left transition-all duration-150 w-full flex items-center gap-2 hover:bg-surface-base hover:border-focus hover:translate-x-0.5 focus-visible:outline-2 focus-visible:outline-accent-primary focus-visible:outline-offset-2"
              onClick={() => onJump(item.id)}
              data-testid={`navigator-${item.id}`}
            >
              <div className={`${getRoleColor(item.role)} text-[10px] font-bold uppercase min-w-[50px] opacity-90`}>
                {item.role.toUpperCase()}
              </div>
              <div className="flex-1 text-xs font-medium overflow-hidden text-ellipsis whitespace-nowrap text-primary">
                {item.title}
              </div>
              <div className="text-[11px] text-tertiary opacity-80 min-w-[70px] text-right">
                {formatTime(item.timestamp)}
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
