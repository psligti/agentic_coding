import { act, renderHook } from '@testing-library/react'
import { useStore } from '../store'

describe('store', () => {
  it('initializes with defaults', () => {
    const { result } = renderHook(() => useStore())

    expect(result.current.sessions).toEqual([])
    expect(result.current.currentSession).toBeNull()
    expect(result.current.messages).toEqual({})
    expect(result.current.drawerTab).toBe('sessions')
    expect(result.current.modelStatus.name).toBe('Agent')
    expect(result.current.agents).toEqual([])
    expect(result.current.tools).toEqual([])
    expect(result.current.skills).toEqual([])
    expect(result.current.models).toEqual([])
    expect(result.current.accounts).toEqual([])
  })

  it('updates selections', () => {
    const { result } = renderHook(() => useStore())

    act(() => {
      result.current.setSelectedAgent('build')
      result.current.setSelectedModel('gpt-4o-mini')
      result.current.setSelectedSkills(['git-master'])
      result.current.setSelectedAccount('default')
    })

    expect(result.current.selectedAgent).toBe('build')
    expect(result.current.selectedModel).toBe('gpt-4o-mini')
    expect(result.current.selectedSkills).toEqual(['git-master'])
    expect(result.current.selectedAccount).toBe('default')
  })
})
