import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useRightDrawer } from '../hooks/useRightDrawer'

describe('useRightDrawer integration', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('initializes from localStorage and updates state', () => {
    // Set localStorage to simulate previous state
    localStorage.setItem('rightDrawerOpen', 'true')

    const { result } = renderHook(() => useRightDrawer())

    expect(result.current.open).toBe(true)
    expect(result.current.setRightDrawerOpen).toBeDefined()
    expect(result.current.toggleRightDrawer).toBeDefined()

    // Toggle and verify
    act(() => {
      result.current.toggleRightDrawer()
    })

    expect(result.current.open).toBe(false)

    // Verify localStorage persistence
    expect(localStorage.getItem('rightDrawerOpen')).toBe('false')
  })

  it('provides correct API for drawer control', () => {
    const { result } = renderHook(() => useRightDrawer())

    // Check all methods exist and are functions
    expect(result.current).toHaveProperty('open')
    expect(result.current).toHaveProperty('setRightDrawerOpen')
    expect(result.current).toHaveProperty('toggleRightDrawer')
    expect(typeof result.current.open).toBe('boolean')
    expect(typeof result.current.setRightDrawerOpen).toBe('function')
    expect(typeof result.current.toggleRightDrawer).toBe('function')

    // Test initial state is closed
    expect(result.current.open).toBe(false)
  })
})
