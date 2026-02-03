import { useCallback } from 'react'
import { useSessions as useSessionsState, useSetCurrentSession, useSetSessions, useCurrentSession } from '../store'
import type { Session } from '../store'
import { fetchApi, deleteApi, postApi, putApi } from './useApiClient'

interface SessionsResponse {
  sessions: Array<{
    id: string
    title: string
    version?: string
    created_at?: string
    updated_at?: string
  }>
  count: number
}

interface SessionResponse {
  id: string
  title: string
  version?: string
  theme_id?: string
  created_at?: string
  updated_at?: string
}

const toTimestamp = (value?: string) => {
  if (!value) return Date.now()
  const timestamp = Date.parse(value)
  return Number.isNaN(timestamp) ? Date.now() : timestamp
}

export function normalizeSession(session: SessionResponse): Session {
  return {
    id: session.id,
    title: session.title,
    time_created: toTimestamp(session.created_at),
    time_updated: toTimestamp(session.updated_at),
    message_count: 0,
    theme_id: session.theme_id,
  }
}

/**
 * Hook to manage sessions with API integration
 * Provides functions to fetch, create, and delete sessions
 */
export function useSessions() {
  const sessions = useSessionsState()
  const setSessions = useSetSessions()
  const setCurrentSession = useSetCurrentSession()
  const currentSession = useCurrentSession()

  /**
   * Fetch all sessions from API
   */
  const fetchSessions = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchApi<SessionsResponse>('/sessions')
      const normalized = response.sessions.map(normalizeSession)
      setSessions(normalized)
    } catch (error) {
      console.error('Failed to fetch sessions:', error)
      throw error
    }
  }, [setSessions])

  /**
   * Create a new session
   */
  const createSession = useCallback(async (title: string = 'New Session'): Promise<Session> => {
    try {
      const session = await postApi<SessionResponse>('/sessions', { title })
      const normalized = normalizeSession(session)
      setSessions([normalized, ...sessions])
      return normalized
    } catch (error) {
      console.error('Failed to create session:', error)
      throw error
    }
  }, [sessions, setSessions])

  /**
   * Delete a session by ID
   */
  const deleteSession = useCallback(async (sessionId: string): Promise<void> => {
    try {
      await deleteApi(`/sessions/${sessionId}`)
      setSessions(sessions.filter((s) => s.id !== sessionId))
      setCurrentSession(null)
    } catch (error) {
      console.error('Failed to delete session:', error)
      throw error
    }
  }, [sessions, setCurrentSession, setSessions])

  /**
   * Update a session by ID (e.g., change theme_id)
   */
  const updateSession = useCallback(async (sessionId: string, updates: Partial<Session>): Promise<Session> => {
    try {
      const updateData = updates.theme_id !== undefined ? { theme_id: updates.theme_id } : undefined

      const response = await putApi<SessionResponse>(`/sessions/${sessionId}`, updateData)
      const normalized = normalizeSession(response)

      setSessions(sessions.map((s) => (s.id === sessionId ? normalized : s)))

      if (currentSession?.id === sessionId) {
        setCurrentSession(normalized)
      }

      return normalized
    } catch (error) {
      console.error('Failed to update session:', error)
      throw error
    }
  }, [sessions, currentSession, setSessions, setCurrentSession])

  return {
    sessions,
    fetchSessions,
    createSession,
    deleteSession,
    updateSession,
  }
}
