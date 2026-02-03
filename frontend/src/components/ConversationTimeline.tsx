import { useEffect, useMemo, useRef, useState } from 'react'
import { MessageCard, type MessageRole } from './MessageCard'
import { useCurrentSession, useMessagesState, type Message } from '../store'
import { useMessages } from '../hooks/useMessages'

function isMessageRole(value: string): value is MessageRole {
  return ['user', 'assistant', 'system', 'tool', 'question', 'thinking', 'error'].includes(value)
}

function groupConsecutiveMessages(messages: Message[]) {
  const groups: Array<{
    id: string
    role: MessageRole
    messages: Message[]
  }> = []

  for (const message of messages) {
    const lastGroup = groups[groups.length - 1]
    const role: MessageRole = isMessageRole(message.role) ? message.role : 'assistant'

    if (lastGroup && lastGroup.role === role) {
      lastGroup.messages.push(message)
    } else {
      groups.push({
        id: message.id,
        role,
        messages: [message],
      })
    }
  }

  return groups
}

export function ConversationTimeline() {
  const currentSession = useCurrentSession()
  const messagesBySession = useMessagesState()
  const { fetchMessages } = useMessages()
  const [isLoading, setIsLoading] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const [, setCanScrollUp] = useState(false)
  const [, setCanScrollDown] = useState(false)

  const messages = useMemo(() => {
    if (!currentSession) return []
    return messagesBySession[currentSession.id] || []
  }, [currentSession, messagesBySession])

  const groupedMessages = useMemo(() => {
    return groupConsecutiveMessages(messages)
  }, [messages])

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
  }, [groupedMessages.length])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const checkScrollPosition = () => {
      const canUp = container.scrollTop > 0
      const canDown = Math.ceil(container.scrollTop + container.clientHeight) < container.scrollHeight
      setCanScrollUp(canUp)
      setCanScrollDown(canDown)
    }

    const timer = setTimeout(() => checkScrollPosition(), 0)
    container.addEventListener('scroll', checkScrollPosition)
    window.addEventListener('resize', checkScrollPosition)

    return () => {
      clearTimeout(timer)
      container.removeEventListener('scroll', checkScrollPosition)
      window.removeEventListener('resize', checkScrollPosition)
    }
  }, [groupedMessages.length, containerRef])

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
      {groupedMessages.length > 0 && (
        <>
          {groupedMessages.map((group) => (
            <MessageCard key={group.id} messages={group.messages} role={group.role} />
          ))}
        </>
      )}
    </div>
  )
}
