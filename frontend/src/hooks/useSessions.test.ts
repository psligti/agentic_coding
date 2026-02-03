import { describe, it, expect } from 'vitest'
import { normalizeSession } from './useSessions'

describe('normalizeSession', () => {
  it('preserves theme_id when provided', () => {
    const input = {
      id: 'session-1',
      title: 'Test Session',
      theme_id: 'aurora',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    }

    const result = normalizeSession(input)

    expect(result).toEqual({
      id: 'session-1',
      title: 'Test Session',
      time_created: Date.parse('2024-01-01T00:00:00Z'),
      time_updated: Date.parse('2024-01-02T00:00:00Z'),
      message_count: 0,
      theme_id: 'aurora',
    })
  })

  it('handles missing theme_id gracefully', () => {
    const input = {
      id: 'session-1',
      title: 'Test Session',
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-02T00:00:00Z',
    }

    const result = normalizeSession(input)

    expect(result).toEqual({
      id: 'session-1',
      title: 'Test Session',
      time_created: Date.parse('2024-01-01T00:00:00Z'),
      time_updated: Date.parse('2024-01-02T00:00:00Z'),
      message_count: 0,
    })

    expect(result.theme_id).toBeUndefined()
  })

  it('handles missing date strings', () => {
    const input = {
      id: 'session-1',
      title: 'Test Session',
      theme_id: 'ember',
    }

    const result = normalizeSession(input)

    expect(result).toEqual({
      id: 'session-1',
      title: 'Test Session',
      time_created: expect.any(Number),
      time_updated: expect.any(Number),
      message_count: 0,
      theme_id: 'ember',
    })

    // Both should be current time when not provided
    expect(result.time_created).toBe(result.time_updated)
  })
})

