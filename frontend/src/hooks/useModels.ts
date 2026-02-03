import { useCallback } from 'react'
import { useModelsState, useSetModels } from '../store'
import type { ModelSummary } from '../types/api'
import { fetchApi } from './useApiClient'

export function useModels() {
  const models = useModelsState()
  const setModels = useSetModels()

  const fetchModels = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchApi<ModelSummary[]>('/models')
      setModels(response)
    } catch (error) {
      console.error('Failed to fetch models:', error)
      throw error
    }
  }, [setModels])

  return {
    models,
    fetchModels,
  }
}
