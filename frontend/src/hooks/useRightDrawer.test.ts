import { describe, it, expect, beforeEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useRightDrawer } from '../hooks/useRightDrawer'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    },
  }
})()

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
})

describe('useRightDrawer', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('initializes with closed state from localStorage', () => {
    // Simulate closed state being stored
    localStorage.setItem('rightDrawerOpen', 'false')

    const { result } = renderHook(() => useRightDrawer())

    expect(result.current.open).toBe(false)
  })

  it('initializes with open state from localStorage', () => {
    // Simulate open state being stored
    localStorage.setItem('rightDrawerOpen', 'true')

    const { result } = renderHook(() => useRightDrawer())

    expect(result.current.open).toBe(true)
  })

  it('initializes to closed state if localStorage is empty', () => {
    const { result } = renderHook(() => useRightDrawer())

    expect(result.current.open).toBe(false)
  })

  it('toggles open state when toggleRightDrawer is called', () => {
    const { result } = renderHook(() => useRightDrawer())

    act(() => {
      result.current.toggleRightDrawer()
    })

    expect(result.current.open).toBe(true)

    act(() => {
      result.current.toggleRightDrawer()
    })

    expect(result.current.open).toBe(false)
  })

  it('sets open state when setRightDrawerOpen is called', () => {
    const { result } = renderHook(() => useRightDrawer())

    act(() => {
      result.current.setRightDrawerOpen(true)
    })

    expect(result.current.open).toBe(true)

    act(() => {
      result.current.setRightDrawerOpen(false)
    })

    expect(result.current.open).toBe(false)
  })

  it('persists open state to localStorage on toggle', () => {
    const { result } = renderHook(() => useRightDrawer())

    act(() => {
      result.current.toggleRightDrawer()
    })

    waitFor(() => {
      expect(localStorage.getItem('rightDrawerOpen')).toBe('true')
    })

    act(() => {
      result.current.toggleRightDrawer()
    })

    waitFor(() => {
      expect(localStorage.getItem('rightDrawerOpen')).toBe('false')
    })
  })

  it('persists open state to localStorage on setRightDrawerOpen', () => {
    const { result } = renderHook(() => useRightDrawer())

    act(() => {
      result.current.setRightDrawerOpen(true)
    })

    waitFor(() => {
      expect(localStorage.getItem('rightDrawerOpen')).toBe('true')
    })

    act(() => {
      result.current.setRightDrawerOpen(false)
    })

    waitFor(() => {
      expect(localStorage.getItem('rightDrawerOpen')).toBe('false')
    })
  })

  it('returns setter function', () => {
    const { result } = renderHook(() => useRightDrawer())

    expect(result.current.setRightDrawerOpen).toBeDefined()
    expect(typeof result.current.setRightDrawerOpen).toBe('function')
  })

  it('returns toggle function', () => {
    const { result } = renderHook(() => useRightDrawer())

    expect(result.current.toggleRightDrawer).toBeDefined()
    expect(typeof result.current.toggleRightDrawer).toBe('function')
  })
})
