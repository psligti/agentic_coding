import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useSessionThemeStream } from './useSessionThemeStream'

const mockSetCurrentSession = vi.fn()

vi.mock('../store', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../store')>()
  const mockGetState = vi.fn(() => ({
    currentSession: { id: 'session-123', title: 'Test Session', time_created: 0, time_updated: 0, message_count: 0 },
  }))
  return {
    ...actual,
    useSetCurrentSession: () => mockSetCurrentSession,
    store: { getState: mockGetState },
  }
})

vi.mock('./useApiClient', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./useApiClient')>()
  return {
    ...actual,
    getApi: vi.fn(),
  }
})

let mockEventSourceInstance: MockEventSource | null = null

class MockEventSource {
  url: string
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  readyState: number = 0

  constructor(url: string) {
    this.url = url
    mockEventSourceInstance = this
  }

  close() {
    this.readyState = 2
  }

  triggerOpen() {
    this.readyState = 1
    this.onopen?.(new Event('open'))
  }

  triggerMessage(data: unknown) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }))
  }

  triggerError() {
    this.readyState = 2
    this.onerror?.(new Event('error'))
  }
}

global.EventSource = MockEventSource as any

describe('useSessionThemeStream', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockEventSourceInstance = null
  })

  it('establishes SSE connection when sessionId is provided', () => {
    const { unmount } = renderHook(() =>
      useSessionThemeStream({ sessionId: 'session-123' })
    )

    expect(mockEventSourceInstance).toBeDefined()
    unmount()
  })

  it('does not connect when sessionId is empty', () => {
    const { unmount } = renderHook(() =>
      useSessionThemeStream({ sessionId: '' })
    )

    expect(mockEventSourceInstance).toBeNull()
    unmount()
  })

  it('disconnects SSE connection on unmount', () => {
    const { unmount } = renderHook(() =>
      useSessionThemeStream({ sessionId: 'session-123' })
    )

    expect(mockEventSourceInstance).toBeDefined()
    unmount()
    expect(mockEventSourceInstance?.readyState).toBe(2)
  })

  it('processes session_theme events by calling setCurrentSession', async () => {
    const { unmount } = renderHook(() =>
      useSessionThemeStream({ sessionId: 'session-123' })
    )

    mockEventSourceInstance?.triggerOpen()
    mockEventSourceInstance?.triggerMessage({
      type: 'session_theme',
      session_id: 'session-123',
      theme_id: 'aurora',
    })

    await waitFor(() => {
      expect(mockSetCurrentSession).toHaveBeenCalled()
    })

    unmount()
  })

  it('ignores theme events for different sessions', async () => {
    const { unmount } = renderHook(() =>
      useSessionThemeStream({ sessionId: 'session-123' })
    )

    mockEventSourceInstance?.triggerOpen()

    mockEventSourceInstance?.triggerMessage({
      type: 'session_theme',
      session_id: 'different-session',
      theme_id: 'midnight',
    })

    await waitFor(() => {
      expect(mockSetCurrentSession).not.toHaveBeenCalled()
    })

    unmount()
  })

  it('handles ping events without errors', async () => {
    const { unmount } = renderHook(() =>
      useSessionThemeStream({ sessionId: 'session-123' })
    )

    mockEventSourceInstance?.triggerOpen()

    expect(() => {
      mockEventSourceInstance?.triggerMessage({
        type: 'ping',
      })
    }).not.toThrow()

    unmount()
  })
})
