import { useCallback } from 'react'
import { useAddMessage, useSetMessages } from '../store'
import { fetchApi } from './useApiClient'
import type { MessageRole } from '../types/api'
import type { Message } from '../store'

interface MessageResponse {
  id: string
  session_id: string
  role: MessageRole
  text: string
  parts: any[]
  time?: Record<string, unknown>
}

const toTimestamp = (time?: Record<string, unknown>) => {
  const created = time?.created
  if (typeof created === 'number') {
    return created * 1000
  }
  return Date.now()
}

/**
 * Hook to manage messages with API integration
 * Provides functions to fetch and add messages
 */
export function useMessages() {
  const addMessage = useAddMessage()
  const setMessages = useSetMessages()

  /**
   * Fetch messages for a session from the API
   */
  const fetchMessages = useCallback(async (sessionId: string): Promise<void> => {
    try {
      const messages = await fetchApi<MessageResponse[]>(`/sessions/${sessionId}/messages`)
      const normalized = messages.map((msg) => ({
        id: msg.id,
        session_id: msg.session_id,
        role: msg.role,
        text: msg.text,
        parts: msg.parts || [],
        timestamp: toTimestamp(msg.time),
      }))
      setMessages(sessionId, normalized)
    } catch (error) {
      console.error('Failed to fetch messages:', error)
      throw error
    }
  }, [setMessages])

  /**
   * Add a new message to a session
   */
  const addMessageToSession = async (
    sessionId: string,
    message: { role: MessageRole; content: string }
  ): Promise<Message> => {
    try {
      const newMessage = await fetchApi<MessageResponse>(`/sessions/${sessionId}/messages`, {
        method: 'POST',
        body: JSON.stringify(message),
      })
      const normalized: Message = {
        id: newMessage.id,
        session_id: newMessage.session_id,
        role: newMessage.role,
        text: newMessage.text,
        parts: newMessage.parts || [],
        timestamp: toTimestamp(newMessage.time),
      }
      addMessage(sessionId, normalized)
      return normalized
    } catch (error) {
      console.error('Failed to add message:', error)
      throw error
    }
  }

  /**
   * Create a user message
   */
  const createUserMessage = async (
    sessionId: string,
    text: string
  ): Promise<Message> => {
    return addMessageToSession(sessionId, { role: 'user', content: text })
  }

  /**
   * Create an assistant message
   */
  const createAssistantMessage = async (
    sessionId: string,
    text: string,
    parts: any[] = []
  ): Promise<Message> => {
    const created = await addMessageToSession(sessionId, { role: 'assistant', content: text })
    if (parts.length > 0) {
      return {
        ...created,
        parts,
      }
    }
    return created
  }

  /**
   * Create a system message
   */
  const createSystemMessage = async (
    sessionId: string,
    text: string
  ): Promise<Message> => {
    return addMessageToSession(sessionId, { role: 'system', content: text })
  }

  return {
    fetchMessages,
    addMessageToSession,
    createUserMessage,
    createAssistantMessage,
    createSystemMessage,
  }
}
