import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ThemePicker from '../components/ThemePicker'

const mockCurrentSession = {
  id: 'session-1',
  title: 'Test Session',
  time_created: Date.now(),
  time_updated: Date.now(),
  message_count: 0,
  theme_id: 'aurora',
}

const mockUpdateSession = vi.fn()

vi.mock('../store', () => ({
  useCurrentSession: () => mockCurrentSession,
}))

vi.mock('../hooks/useSessions', () => ({
  useSessions: () => ({
    sessions: [],
    updateSession: mockUpdateSession,
  }),
}))

describe('ThemePicker', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('displays theme options with labels and descriptions', () => {
    render(<ThemePicker />)

    expect(screen.getByText('Aurora')).toBeInTheDocument()
    expect(screen.getByText('Purple and indigo gradients')).toBeInTheDocument()
    expect(screen.getByText('Ocean')).toBeInTheDocument()
    expect(screen.getByText('Teal and cyan depths')).toBeInTheDocument()
    expect(screen.getByText('Ember')).toBeInTheDocument()
    expect(screen.getByText('Warm amber and orange glow')).toBeInTheDocument()
  })

  it('calls updateSession when Ocean theme is selected', async () => {
    render(<ThemePicker />)

    const oceanButton = screen.getByLabelText('Select Ocean theme')
    fireEvent.click(oceanButton)

    await waitFor(() => {
      expect(mockUpdateSession).toHaveBeenCalledWith('session-1', { theme_id: 'ocean' })
    })
  })

  it('calls updateSession when Ember theme is selected', async () => {
    render(<ThemePicker />)

    const emberButton = screen.getByLabelText('Select Ember theme')
    fireEvent.click(emberButton)

    await waitFor(() => {
      expect(mockUpdateSession).toHaveBeenCalledWith('session-1', { theme_id: 'ember' })
    })
  })

  it('does not call updateSession when same theme is clicked', () => {
    render(<ThemePicker />)

    const auroraButton = screen.getByLabelText('Select Aurora theme')
    fireEvent.click(auroraButton)

    expect(mockUpdateSession).not.toHaveBeenCalled()
  })

  it('shows active indicator for current theme', () => {
    render(<ThemePicker />)

    const auroraButton = screen.getByLabelText('Select Aurora theme')
    const activeIndicator = auroraButton.querySelector('.theme-picker__active')

    expect(activeIndicator).toBeInTheDocument()
    expect(activeIndicator?.textContent).toBe('✓')
  })
})
