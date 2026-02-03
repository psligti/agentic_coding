import { useCallback } from 'react'
import { useSetTools, useToolsState } from '../store'
import type { ToolSummary } from '../types/api'
import { fetchApi } from './useApiClient'

export function useTools() {
  const tools = useToolsState()
  const setTools = useSetTools()

  const fetchTools = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchApi<ToolSummary[]>('/tools')
      setTools(response)
    } catch (error) {
      console.error('Failed to fetch tools:', error)
      throw error
    }
  }, [setTools])

  return {
    tools,
    fetchTools,
  }
}
