import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import * as Icons from 'lucide-react'
import './MessageCard.css'

type MessageRole = 'user' | 'assistant' | 'system' | 'tool' | 'question' | 'thinking' | 'error'

interface MessageCardProps {
  message: {
    id: string
    role: MessageRole
    text: string
    parts: any[]
    timestamp?: number
  }
  onCopy?: () => void
  onQuote?: () => void
  onEdit?: () => void
}

/**
 * MessageCard component for rendering individual messages in the timeline
 * Supports 7 message types with proper styling and action buttons
 */
export function MessageCard({
  message,
  onCopy,
  onQuote,
  onEdit,
}: MessageCardProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(message.text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    onCopy?.()
  }

  const handleQuote = () => {
    onQuote?.()
  }

  const handleEdit = () => {
    onEdit?.()
  }

  const renderIcon = () => {
    switch (message.role) {
      case 'user':
        return <Icons.User size={14} data-testid={`${message.role}-icon`} />
      case 'assistant':
        return <Icons.Bot size={14} data-testid={`${message.role}-icon`} />
      case 'system':
        return <Icons.Info size={14} data-testid={`${message.role}-icon`} />
      case 'tool':
        return <Icons.Wrench size={14} data-testid={`${message.role}-icon`} />
      case 'question':
        return <Icons.HelpCircle size={14} data-testid={`${message.role}-icon`} />
      case 'thinking':
        return <Icons.Sparkles size={14} data-testid={`${message.role}-icon`} />
      case 'error':
        return <Icons.AlertCircle size={14} data-testid={`${message.role}-icon`} />
      default:
        return null
    }
  }

  return (
    <div className={`message-card message-card--${message.role}`} id={`message-${message.id}`}>
      <div className="message-card__header">
        <div className="message-card__role">
          {renderIcon()}
          <span>{message.role.charAt(0).toUpperCase() + message.role.slice(1)}</span>
        </div>
        <span className="message-card__timestamp">
          {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : 'Just now'}
        </span>
      </div>

      <div className="message-card__body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {message.text}
        </ReactMarkdown>
      </div>

      <div className="message-card__footer">
        <button
          className="message-card__action"
          onClick={handleCopy}
          title={copied ? 'Copied!' : 'Copy message'}
        >
          <Icons.Copy size={14} />
          {copied ? 'Copied' : 'Copy'}
        </button>
        {onQuote && (
          <button
            className="message-card__action"
            onClick={handleQuote}
            title="Quote message"
          >
            <Icons.Quote size={14} />
            Quote
          </button>
        )}
        {message.role === 'assistant' && onEdit && (
          <button
            className="message-card__action"
            onClick={handleEdit}
            title="Edit message"
          >
            <Icons.Edit size={14} />
            Edit
          </button>
        )}
      </div>
    </div>
  )
}
