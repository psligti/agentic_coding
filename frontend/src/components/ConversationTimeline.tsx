import { useEffect, useMemo, useRef, useState } from 'react'
import { MessageCard } from './MessageCard'
import { useCurrentSession, useMessagesState } from '../store'
import { useMessages } from '../hooks/useMessages'

export function ConversationTimeline() {
  const currentSession = useCurrentSession()
  const messagesBySession = useMessagesState()
  const { fetchMessages } = useMessages()
  const [isLoading, setIsLoading] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  const messages = useMemo(() => {
    if (!currentSession) return []
    return messagesBySession[currentSession.id] || []
  }, [currentSession, messagesBySession])

  useEffect(() => {
    if (!currentSession) return

    let isMounted = true
    setIsLoading(true)
    fetchMessages(currentSession.id)
      .catch((error) => {
        console.error('Failed to load messages:', error)
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [currentSession, fetchMessages])

  useEffect(() => {
    if (!containerRef.current) return
    containerRef.current.scrollTop = containerRef.current.scrollHeight
  }, [messages.length])

  return (
    <div
      ref={containerRef}
      className="timeline-container"
      data-loading={isLoading}
    >
      {isLoading && <div className="timeline-loading">Loading messages...</div>}
      {!currentSession && !isLoading && (
        <div className="timeline-empty">No active session. Create one to start chatting.</div>
      )}
      {currentSession && messages.length === 0 && !isLoading && (
        <div className="timeline-empty">No messages yet. Start a conversation!</div>
      )}
      {messages.length > 0 && (
        <div className="timeline-messages">
          {messages.map((message) => (
            <div key={message.id} className="timeline-message">
              <MessageCard message={message} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
