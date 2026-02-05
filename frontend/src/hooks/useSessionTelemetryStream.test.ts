import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSessionTelemetryStream } from './useSessionTelemetryStream'
import { getApi } from './useApiClient'

const mockSetTelemetry = vi.fn()

vi.mock('../store', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../store')>()
  const mockGetState = vi.fn(() => ({
    currentSession: { id: 'session-123', title: 'Test Session', time_created: 0, time_updated: 0, message_count: 0 },
  }))
  return {
    ...actual,
    useSetTelemetry: () => mockSetTelemetry,
    store: { getState: mockGetState },
  }
})

vi.mock('./useApiClient', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./useApiClient')>()
  const mockGetApi = vi.fn().mockResolvedValue({
    git: { is_repo: true, branch: 'main', dirty_count: 0, staged_count: 0 },
    tools: { running: null, last: null, recent: [] },
    effort: { duration_ms: 0, token_total: 0, tool_count: 0, effort_score: 0 },
  })
  return {
    ...actual,
    getApi: mockGetApi,
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

describe('useSessionTelemetryStream', () => {
  const mockedGetApi = vi.mocked(getApi)

  beforeEach(() => {
    vi.clearAllMocks()
    mockEventSourceInstance = null
    vi.useFakeTimers()
    mockedGetApi.mockResolvedValue({
      git: { is_repo: true, branch: 'main', dirty_count: 0, staged_count: 0 },
      tools: { running: null, last: null, recent: [] },
      effort: { duration_ms: 0, token_total: 0, tool_count: 0, effort_score: 0 },
    })
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('establishes SSE connection when sessionId is provided', () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    expect(mockEventSourceInstance).toBeDefined()
    unmount()
  })

  it('does not connect when sessionId is empty', () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: '' })
    )

    expect(mockEventSourceInstance).toBeNull()
    unmount()
  })

  it('disconnects SSE connection on unmount', () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    expect(mockEventSourceInstance).toBeDefined()
    unmount()
    expect(mockEventSourceInstance?.readyState).toBe(2)
  })

  it('processes telemetry events by calling setTelemetry', async () => {
    const mockTelemetry = {
      git: { is_repo: true, branch: 'main', dirty_count: 2, staged_count: 1 },
      tools: { running: null, last: { tool_id: 'bash', status: 'success' }, recent: [] },
      effort: { duration_ms: 60000, token_total: 1000, tool_count: 5, effort_score: 2 },
    }

    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    await act(async () => {
      mockEventSourceInstance?.triggerOpen()
    })

    act(() => {
      mockEventSourceInstance?.triggerMessage({
        type: 'telemetry',
        session_id: 'session-123',
        telemetry: mockTelemetry,
      })
    })

    expect(mockSetTelemetry).toHaveBeenCalledWith(mockTelemetry)

    unmount()
  })

  it('ignores telemetry events for different sessions', async () => {
    const mockTelemetry = {
      git: { is_repo: true, branch: 'main', dirty_count: 0, staged_count: 0 },
      tools: { running: null, last: null, recent: [] },
      effort: { duration_ms: 0, token_total: 0, tool_count: 0, effort_score: 0 },
    }

    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    await act(async () => {
      mockEventSourceInstance?.triggerOpen()
    })

    mockSetTelemetry.mockClear()

    act(() => {
      mockEventSourceInstance?.triggerMessage({
        type: 'telemetry',
        session_id: 'different-session',
        telemetry: mockTelemetry,
      })
    })

    expect(mockSetTelemetry).not.toHaveBeenCalled()

    unmount()
  })

  it('handles ping events without errors', async () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    await act(async () => {
      mockEventSourceInstance?.triggerOpen()
    })

    expect(() => {
      mockEventSourceInstance?.triggerMessage({
        type: 'ping',
      })
    }).not.toThrow()

    unmount()
  })

  it('handles session_theme events without errors', async () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    await act(async () => {
      mockEventSourceInstance?.triggerOpen()
    })

    mockSetTelemetry.mockClear()

    act(() => {
      mockEventSourceInstance?.triggerMessage({
        type: 'session_theme',
        session_id: 'session-123',
        theme_id: 'aurora',
      })
    })

    expect(mockSetTelemetry).not.toHaveBeenCalled()

    unmount()
  })

  it('refetches telemetry snapshot on connection open', async () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    await act(async () => {
      mockEventSourceInstance?.triggerOpen()
    })

    expect(mockSetTelemetry).toHaveBeenCalled()

    unmount()
  })

  it('reconnects with exponential backoff on error', async () => {
    let oldInstance = mockEventSourceInstance
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    await act(async () => {
      mockEventSourceInstance?.triggerOpen()
      mockEventSourceInstance?.triggerError()
    })

    await act(async () => {
      vi.advanceTimersByTime(1000)
    })

    expect(mockEventSourceInstance).not.toBe(oldInstance)

    unmount()
  })

  it('uses increasing backoff delays across consecutive failures', async () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    const firstInstance = mockEventSourceInstance
    await act(async () => {
      firstInstance?.triggerOpen()
      firstInstance?.triggerError()
    })

    await act(async () => {
      vi.advanceTimersByTime(1000)
    })

    const secondInstance = mockEventSourceInstance
    expect(secondInstance).not.toBe(firstInstance)

    await act(async () => {
      secondInstance?.triggerError()
    })

    await act(async () => {
      vi.advanceTimersByTime(1000)
    })
    expect(mockEventSourceInstance).toBe(secondInstance)

    await act(async () => {
      vi.advanceTimersByTime(1000)
    })
    expect(mockEventSourceInstance).not.toBe(secondInstance)

    unmount()
  })

  it('does not reconnect when session is not found (404)', async () => {
    mockedGetApi.mockImplementation(async (endpoint: string) => {
      if (endpoint === '/sessions/session-123') {
        throw { status: 404, message: 'Session not found' }
      }
      return {
        git: { is_repo: true, branch: 'main', dirty_count: 0, staged_count: 0 },
        tools: { running: null, last: null, recent: [] },
        effort: { duration_ms: 0, token_total: 0, tool_count: 0, effort_score: 0 },
      }
    })

    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    const oldInstance = mockEventSourceInstance
    await act(async () => {
      oldInstance?.triggerOpen()
      oldInstance?.triggerError()
    })

    await act(async () => {
      vi.advanceTimersByTime(10000)
    })

    expect(mockEventSourceInstance).toBe(oldInstance)

    unmount()
  })

  it('stops reconnecting after max retries', async () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123', maxRetries: 2 })
    )

    for (let i = 0; i < 3; i++) {
      mockEventSourceInstance?.triggerOpen()
      mockEventSourceInstance?.triggerError()

      if (i < 2) {
        const delay = Math.pow(2, i) * 1000
        act(() => {
          vi.advanceTimersByTime(delay)
        })
      }
    }

    act(() => {
      vi.advanceTimersByTime(10000)
    })

    unmount()
  })

  it('clears reconnect timeout on unmount', async () => {
    const { unmount } = renderHook(() =>
      useSessionTelemetryStream({ sessionId: 'session-123' })
    )

    mockEventSourceInstance?.triggerOpen()
    mockEventSourceInstance?.triggerError()

    unmount()

    act(() => {
      vi.advanceTimersByTime(2000)
    })

    expect(mockEventSourceInstance?.readyState).toBe(2)
  })
})
