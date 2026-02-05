import { useEffect, useRef } from 'react'
import type { Session } from '../store'
import { getApi, type ApiError } from './useApiClient'
import { useSetCurrentSession } from '../store'
import { store } from '../store'

/**
 * SSE event types from the backend for session updates
 */
type SessionSSEEventType =
  | 'session_theme'
  | 'ping'

/**
 * SSE event data structure for session updates
 */
interface SessionSSEEvent {
  type: SessionSSEEventType
  session_id?: string
  theme_id?: string
}

/**
 * Hook options for session theme stream connection
 */
export interface UseSessionThemeStreamOptions {
  sessionId: string
  maxRetries?: number
}

/**
 * Hook to subscribe to session theme changes via SSE streaming
 * Manages connection, reconnection with exponential backoff, and event handling
 * Refetches the session on reconnect to avoid stale theme state
 */
export function useSessionThemeStream(options: UseSessionThemeStreamOptions) {
  const {
    sessionId,
    maxRetries = 5,
  } = options

  const eventSourceRef = useRef<EventSource | null>(null)
  const retryCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const isConnectingRef = useRef(false)
  const isActiveRef = useRef(true)
  const setCurrentSession = useSetCurrentSession()

  /**
   * Fetch the current session from API to get the latest theme_id
   * Used on reconnect to avoid stale theme state
   */
  const refetchSession = async () => {
    try {
      const response = await getApi<{
        id: string
        title: string
        theme_id?: string
        created_at?: string
        updated_at?: string
      }>(`/sessions/${sessionId}`)

      // Normalize the session response
      const toTimestamp = (value?: string) => {
        if (!value) return Date.now()
        const timestamp = Date.parse(value)
        return Number.isNaN(timestamp) ? Date.now() : timestamp
      }

      const currentSession = store.getState().currentSession
      const session: Session = {
        id: response.id,
        title: response.title,
        time_created: toTimestamp(response.created_at),
        time_updated: toTimestamp(response.updated_at),
        message_count: 0,
        theme_id: response.theme_id,
      }

      if (currentSession?.id === sessionId) {
        setCurrentSession(session)
        console.log('Refetched session with theme_id:', session.theme_id)
      }
    } catch (error) {
      console.error('Failed to refetch session:', error)
    }
  }

  /**
   * Connect to SSE endpoint with exponential backoff reconnection
   */
  const connect = () => {
    if (eventSourceRef.current || isConnectingRef.current) {
      return
    }

    isConnectingRef.current = true

    const sseUrl = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/sessions/${sessionId}/stream`

    try {
      const eventSource = new EventSource(sseUrl)
      eventSourceRef.current = eventSource

      eventSource.onopen = () => {
        isConnectingRef.current = false
        retryCountRef.current = 0
        console.log('Session theme SSE connected:', sseUrl)

        // Refetch session on reconnect to get latest theme_id
        refetchSession()
      }

      eventSource.onmessage = (event) => {
        try {
          const data: SessionSSEEvent = JSON.parse(event.data)

          switch (data.type) {
            case 'session_theme':
              if (data.session_id === sessionId && data.theme_id !== undefined) {
                const currentSession = store.getState().currentSession
                if (currentSession?.id === sessionId) {
                  setCurrentSession({ ...currentSession, theme_id: data.theme_id })
                  console.log('Session theme updated:', data.theme_id)
                }
              }
              break

            case 'ping':
              // Keep-alive ping, do nothing
              break
          }
        } catch (error) {
          console.error('Failed to parse SSE event:', error)
        }
      }

      eventSource.onerror = async (error) => {
        console.error('Session theme SSE connection error:', error)
        isConnectingRef.current = false

        if (eventSourceRef.current) {
          eventSourceRef.current.close()
          eventSourceRef.current = null
        }

        if (!isActiveRef.current) {
          return
        }

        try {
          await getApi(`/sessions/${sessionId}`)
        } catch (sessionError) {
          const apiError = sessionError as ApiError
          if (apiError.status === 404) {
            console.warn(`Stopping theme SSE reconnect: session not found (${sessionId})`)
            return
          }
        }

        // Attempt reconnection with exponential backoff
        if (retryCountRef.current < maxRetries) {
          const retryDelay = Math.pow(2, retryCountRef.current) * 1000 // 1s, 2s, 4s, 8s, 16s

          reconnectTimeoutRef.current = setTimeout(() => {
            if (!isActiveRef.current) {
              return
            }
            retryCountRef.current++
            console.log(`Attempting session theme SSE reconnection (attempt ${retryCountRef.current}/${maxRetries})`)
            connect()
          }, retryDelay)
        } else {
          console.error('Max session theme SSE reconnection attempts reached')
        }
      }
    } catch (error) {
      isConnectingRef.current = false
      console.error('Failed to connect to session theme SSE stream:', error)
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
  }

  // Auto-connect when sessionId is available
  useEffect(() => {
    if (!sessionId) return
    isActiveRef.current = true

    connect()

    return () => {
      isActiveRef.current = false
      disconnect()
    }
  }, [sessionId])

  return {
    connect,
    disconnect,
  }
}
