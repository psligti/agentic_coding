import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import * as Icons from 'lucide-react'

export type MessageRole = 'user' | 'assistant' | 'system' | 'tool' | 'question' | 'thinking' | 'error'

export type { MessageCardProps }

interface MessageCardProps {
  messages: Array<{
    id: string
    role: MessageRole
    text: string
    parts: any[]
    timestamp?: number
  }>
  role: MessageRole
  onCopy?: () => void
  onQuote?: () => void
  onEdit?: () => void
}

/**
 * MessageCard component for rendering grouped messages in the timeline
 * Supports 7 message types with proper styling and action buttons
 * Each message in the group gets its own user pill, timestamp, and copy button
 */
export function MessageCard({
  messages,
  role,
  onCopy,
  onQuote,
  onEdit,
}: MessageCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [canScrollUp, setCanScrollUp] = useState(false)
  const [canScrollDown, setCanScrollDown] = useState(false)
  const [copiedMap, setCopiedMap] = useState<Record<string, boolean>>({})

  useEffect(() => {
    const card = cardRef.current
    if (!card) return

    const checkScrollPosition = () => {
      const canUp = card.scrollTop > 0
      const canDown = Math.ceil(card.scrollTop + card.clientHeight) < card.scrollHeight
      setCanScrollUp(canUp)
      setCanScrollDown(canDown)
    }

    const timer = setTimeout(() => checkScrollPosition(), 0)
    card.addEventListener('scroll', checkScrollPosition)
    window.addEventListener('resize', checkScrollPosition)

    return () => {
      clearTimeout(timer)
      card.removeEventListener('scroll', checkScrollPosition)
      window.removeEventListener('resize', checkScrollPosition)
    }
  }, [messages])

  const handleCopy = (messageId: string, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedMap((prev) => ({ ...prev, [messageId]: true }))
    setTimeout(() => {
      setCopiedMap((prev) => ({ ...prev, [messageId]: false }))
    }, 2000)
    onCopy?.()
  }

  const handleQuote = () => {
    onQuote?.()
  }

  const handleEdit = () => {
    onEdit?.()
  }

  const renderIcon = () => {
    switch (role) {
      case 'user':
        return <Icons.User size={14} data-testid={`${role}-icon`} />
      case 'assistant':
        return <Icons.Bot size={14} data-testid={`${role}-icon`} />
      case 'system':
        return <Icons.Info size={14} data-testid={`${role}-icon`} />
      case 'tool':
        return <Icons.Wrench size={14} data-testid={`${role}-icon`} />
      case 'question':
        return <Icons.HelpCircle size={14} data-testid={`${role}-icon`} />
      case 'thinking':
        return <Icons.Sparkles size={14} data-testid={`${role}-icon`} />
      case 'error':
        return <Icons.AlertCircle size={14} data-testid={`${role}-icon`} />
      default:
        return null
    }
  }

  return (
    <div
      ref={cardRef}
      className={`
        relative w-full min-w-0 max-w-full overflow-y-auto overflow-x-hidden max-h-[400px]
        bg-surface-panel border border-border-normal rounded-lg p-3
        flex flex-col gap-2
        transition-[border-color,box-shadow] duration-200 ease-out
        hover:border-border-focus hover:shadow-[0_0_0_2px_rgba(99,102,241,0.2)]
        ${role === 'error' ? 'border-error bg-[rgba(255,92,122,0.1)]' : ''}
        ${role === 'thinking' ? 'bg-surface-raised border-border-normal' : ''}
      `}
    >
      <div
        className="sticky left-4 right-0 h-8 pointer-events-none z-10 -mt-[1px]"
        style={{ display: canScrollUp ? 'block' : 'none' }}
      >
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(to bottom, transparent 0%, transparent 14px, var(--accent-primary) 14px, var(--accent-primary) 16px, transparent 16px)',
          }}
        />
      </div>

      <div
        className="sticky left-4 right-0 h-8 pointer-events-none z-10 -mb-[1px]"
        style={{ display: canScrollDown ? 'block' : 'none' }}
      >
        <div
          className="absolute inset-0"
          style={{
            background: 'linear-gradient(to top, transparent 0%, transparent 14px, var(--accent-primary) 14px, var(--accent-primary) 16px, transparent 16px)',
          }}
        />
      </div>

      {messages.map((message) => (
        <div key={message.id} className="relative py-3 my-2 min-w-0 max-w-full last:pb-0">
          <div
            className={`
              absolute top-3 left-0 z-10 px-3 py-0.5 rounded-full
              flex items-center gap-1
              bg-surface-panel border border-border-normal
              text-[11px] font-semibold
              ${role === 'error' ? 'text-error border-error' : 'text-text-primary'}
            `}
          >
            <svg width="12" height="12">{renderIcon()}</svg>
            <span>{role.charAt(0).toUpperCase() + role.slice(1)}</span>
          </div>

          <div className="absolute top-3 right-0 flex items-center gap-2 z-10">
            <button
              className="p-1.5 opacity-0 invisible transition-opacity duration-200 ease-out
                bg-transparent border-0 hover:opacity-100 hover:visible
                group-hover:opacity-100 group-hover:visible"
              onClick={() => handleCopy(message.id, message.text)}
              title={copiedMap[message.id] ? 'Copied!' : 'Copy message'}
            >
              <Icons.Copy size={14} />
            </button>
          </div>

          {copiedMap[message.id] && (
            <span className="absolute right-8 top-3 z-10 text-[11px] text-success font-medium animate-fade-in">
              Copied
            </span>
          )}

          <div
            className={`
              text-primary whitespace-pre-wrap break-words overflow-wrap-break-word break-word
              leading-relaxed mt-4 mb-4 min-w-0 max-w-full overflow-x-hidden
              [&_p]:m-0 [&_p]:mb-2 [&_p]:min-w-0 [&_p]:max-w-full [&_p]:overflow-hidden
              [&_p:last-child]:m-0
              [&_pre]:bg-surface-raised [&_pre]:rounded-lg [&_pre]:p-3 [&_pre]:my-2
              [&_pre]:overflow-auto [&_pre]:max-w-full [&_pre]:min-w-0
              [&_pre]:whitespace-pre-wrap [&_pre]:break-words
              [&_code]:font-mono [&_code]:text-[13px]
              [&_:not(pre)>code]:bg-surface-raised [&_:not(pre)>code]:px-1 [&_:not(pre)>code]:py-0.5 [&_:not(pre)>code]:rounded
              ${role === 'user' ? 'text-right text-text-primary' : ''}
              ${role === 'assistant' ? 'text-right text-text-secondary' : ''}
              ${role === 'system' ? 'text-right text-text-tertiary' : ''}
              ${role === 'tool' ? 'text-right text-text-tertiary' : ''}
              ${role === 'question' ? 'text-right text-text-primary' : ''}
              ${role === 'thinking' ? 'text-right text-text-secondary' : ''}
              ${role === 'error' ? 'text-text-primary' : ''}
            `}
          >
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.text}
            </ReactMarkdown>
          </div>

          <span className="absolute bottom-3 right-0 z-10 text-[10px] text-text-tertiary bg-surface-panel px-1 py-0.5 rounded">
            {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'Just now'}
          </span>
        </div>
      ))}

      <div className="mt-2 flex gap-2 opacity-40 transition-opacity duration-200 ease-out hover:opacity-100 focus-within:opacity-100">
        {onQuote && (
          <button
            className="bg-surface-raised border border-border-normal rounded-lg px-3 py-1.5
              text-[12px] cursor-pointer text-text-primary flex items-center
              transition-all duration-200 ease-out
              hover:border-border-focus hover:bg-surface-panel
              focus:outline-none focus:border-border-focus focus:shadow-[0_0_0_2px_rgba(99,102,241,0.2)]
              focus-visible:outline-2 focus-visible:outline-border-focus focus-visible:outline-offset-2"
            onClick={handleQuote}
            title="Quote message"
          >
            <Icons.Quote size={14} />
          </button>
        )}
        {role === 'assistant' && onEdit && (
          <button
            className="bg-surface-raised border border-border-normal rounded-lg px-3 py-1.5
              text-[12px] cursor-pointer text-text-primary flex items-center
              transition-all duration-200 ease-out
              hover:border-border-focus hover:bg-surface-panel
              focus:outline-none focus:border-border-focus focus:shadow-[0_0_0_2px_rgba(99,102,241,0.2)]
              focus-visible:outline-2 focus-visible:outline-border-focus focus-visible:outline-offset-2"
            onClick={handleEdit}
            title="Edit message"
          >
            <Icons.Edit size={14} />
          </button>
        )}
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateX(-5px); }
          to { opacity: 1; transform: translateX(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.2s ease;
        }
        @media (prefers-reduced-motion: reduce) {
          .animate-fade-in {
            animation: none;
          }
        }
      `}</style>
    </div>
  )
}
