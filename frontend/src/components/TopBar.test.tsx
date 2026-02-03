import { render, screen } from '@testing-library/react'
import { TopBar } from './TopBar'

vi.mock('../hooks/useExecuteAgent', () => ({
  useExecuteAgent: () => ({
    execute: vi.fn(),
    stop: vi.fn(),
  }),
}))

vi.mock('../store', () => ({
  useCurrentSession: () => ({
    id: 'session-1',
    title: 'Session 1',
    time_created: 0,
    time_updated: 0,
    message_count: 0,
  }),
  useModelStatus: () => ({ name: 'Agent', connected: true }),
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
  useSelectedModel: () => 'gpt-4o-mini',
  useSelectedSkills: () => [],
}))

describe('TopBar', () => {
  it('renders the OpenCode logo and session title', () => {
    render(<TopBar />)
    expect(screen.getByText('OpenCode')).toBeInTheDocument()
    expect(screen.getByText('Session 1')).toBeInTheDocument()
  })

  it('shows run and stop buttons when session exists', () => {
    render(<TopBar />)
    expect(screen.getByText('Run')).toBeInTheDocument()
    expect(screen.getByText('Stop')).toBeInTheDocument()
  })
})
