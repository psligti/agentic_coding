import { useEffect, useRef } from 'react'
import type { Message } from '../store'
import { postApi } from './useApiClient'
import { useAddMessage, useSetComposerSending } from '../store'

/**
 * SSE event types from the backend
 */
type SSEEventType =
  | 'message'
  | 'start'
  | 'stop'
  | 'error'
  | 'ping'
  | 'finish'

/**
 * SSE event data structure
 */
interface SSEEvent {
  type: SSEEventType
  data?: Record<string, unknown>
  role?: 'user' | 'assistant' | 'system'
  content?: string
}

/**
 * Hook options for SSE connection
 */
export interface UseExecuteAgentOptions {
  sessionId: string
  onStatusChange?: (status: 'idle' | 'connected' | 'connecting' | 'running' | 'error') => void
  maxRetries?: number
}

/**
 * Hook to execute agents with SSE streaming
 * Manages connection, reconnection with exponential backoff, and event handling
 */
export function useExecuteAgent(options: UseExecuteAgentOptions) {
  const {
    sessionId,
    onStatusChange,
    maxRetries = 5,
  } = options

  const eventSourceRef = useRef<EventSource | null>(null)
  const retryCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isConnectingRef = useRef(false)
  const addMessage = useAddMessage()
  const setComposerSending = useSetComposerSending()

  /**
   * Connect to SSE endpoint with exponential backoff reconnection
   */
  const connect = () => {
    if (eventSourceRef.current || isConnectingRef.current) {
      return
    }

    isConnectingRef.current = true
    retryCountRef.current = 0
    onStatusChange?.('connecting')

    const sseUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/tasks/${sessionId}/stream`

    try {
      const eventSource = new EventSource(sseUrl)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        isConnectingRef.current = false
        retryCountRef.current = 0
        onStatusChange?.('connected')
        console.log('SSE connected:', sseUrl)
      }

      eventSource.onmessage = (event) => {
        try {
            const data: SSEEvent = JSON.parse(event.data)

          switch (data.type) {
            case 'start':
              onStatusChange?.('running')
              break

            case 'message':
              if (data.content) {
                const newMessage: Message = {
                  id: `msg-${Date.now()}`,
                  session_id: sessionId,
                  role: data.role || 'assistant',
                  text: data.content,
                  parts: [],
                  timestamp: Date.now(),
                }
                addMessage(sessionId, newMessage)
              }
              break

            case 'finish':
              onStatusChange?.('idle')
              disconnect()
              break

            case 'error':
              onStatusChange?.('error')
              console.error('SSE error event received')
              disconnect()
              break

            case 'ping':
              // Keep-alive ping, do nothing
              break
          }
        } catch (error) {
          console.error('Failed to parse SSE event:', error)
        }
      }

      eventSource.onerror = (error) => {
        console.error('SSE connection error:', error)
        isConnectingRef.current = false
        onStatusChange?.('error')

        if (eventSourceRef.current) {
          eventSourceRef.current.close()
          eventSourceRef.current = null
        }

        // Attempt reconnection with exponential backoff
        if (retryCountRef.current < maxRetries) {
          const retryDelay = Math.pow(2, retryCountRef.current) * 1000 // 1s, 2s, 4s, 8s, 16s

          reconnectTimeoutRef.current = setTimeout(() => {
            retryCountRef.current++
            console.log(`Attempting reconnection (attempt ${retryCountRef.current}/${maxRetries})`)
            connect()
          }, retryDelay)
        } else {
          console.error('Max reconnection attempts reached')
        }
      }
    } catch (error) {
      isConnectingRef.current = false
      onStatusChange?.('error')
      console.error('Failed to connect to SSE stream:', error)
    }
  }

  /**
   * Disconnect SSE connection
   */
  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    isConnectingRef.current = false
    onStatusChange?.('idle')
    setComposerSending(false)
  }

  /**
   * Execute agent with POST request
   */
  const execute = async (
    agentName: string,
    userMessage: string,
    options?: Record<string, unknown>
  ) => {
    try {
      onStatusChange?.('connecting')
      setComposerSending(true)

      await postApi(`/sessions/${sessionId}/execute`, {
        agent_name: agentName,
        user_message: userMessage,
        options,
      })

      // Connect to SSE stream
      connect()
    } catch (error) {
      onStatusChange?.('error')
      console.error('Failed to execute agent:', error)
      setComposerSending(false)
      throw error
    }
  }

  /**
   * Stop agent execution
   */
  const stop = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    isConnectingRef.current = false
    onStatusChange?.('idle')
    setComposerSending(false)
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [sessionId])

  return {
    connect,
    disconnect,
    execute,
    stop,
    isConnected: eventSourceRef.current !== null,
    isConnecting: isConnectingRef.current,
  }
}
