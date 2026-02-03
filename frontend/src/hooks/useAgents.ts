import { useCallback } from 'react'
import { useAgentsState, useSetAgents } from '../store'
import type { AgentSummary } from '../types/api'
import { fetchApi } from './useApiClient'

export function useAgents() {
  const agents = useAgentsState()
  const setAgents = useSetAgents()

  const fetchAgents = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchApi<AgentSummary[]>('/agents')
      setAgents(response)
    } catch (error) {
      console.error('Failed to fetch agents:', error)
      throw error
    }
  }, [setAgents])

  return {
    agents,
    fetchAgents,
  }
}
