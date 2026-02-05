import { useCallback } from 'react'
import { useSetSkills, useSkillsState } from '../store'
import type { SkillSummary } from '../types/api'
import { fetchApi } from './useApiClient'

export function useSkills() {
  const skills = useSkillsState()
  const setSkills = useSetSkills()

  const fetchSkills = useCallback(async (): Promise<void> => {
    try {
      const response = await fetchApi<SkillSummary[]>('/skills')
      setSkills(response)
    } catch (error) {
      throw error
    }
  }, [setSkills])

  return {
    skills,
    fetchSkills,
  }
}
