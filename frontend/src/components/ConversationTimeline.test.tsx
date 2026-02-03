import { render, screen } from '@testing-library/react'
import { ConversationTimeline } from './ConversationTimeline'

vi.mock('../store', () => ({
  useCurrentSession: () => ({
    id: 'session-1',
    title: 'Session 1',
    time_created: 0,
    time_updated: 0,
    message_count: 1,
  }),
  useModelStatus: () => ({ name: 'Agent', connected: true }),
  useMemoryUsage: () => ({ used: 0, total: 8 }),
  useTokenUsage: () => ({ input: 0, output: 0, total: 0, limit: 0 }),
  useMessagesState: () => ({
    'session-1': [
      {
        id: 'msg-1',
        session_id: 'session-1',
        role: 'user',
        text: 'Hello',
        parts: [],
        timestamp: Date.now(),
      },
    ],
  }),
  useSelectedAgent: () => 'build',
  useSelectedModel: () => null,
  useSelectedSkills: () => [],
}))

vi.mock('../hooks/useMessages', () => ({
  useMessages: () => ({
    fetchMessages: () => Promise.resolve(),
  }),
}))

vi.mock('../hooks/useExecuteAgent', () => ({
  useExecuteAgent: () => ({
    execute: vi.fn(),
    stop: vi.fn(),
  }),
}))

describe('ConversationTimeline', () => {
  it('renders messages for current session', () => {
    render(<ConversationTimeline />)
    expect(screen.getByText('Hello')).toBeInTheDocument()
  })
})
