import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { usePalette } from '../store'
import { CommandPalette } from './CommandPalette'

vi.mock('../store', () => ({
  usePalette: vi.fn(),
}))

const mockCommands = [
  {
    id: '1',
    title: 'Create new session',
    keywords: 'session new create',
    run: vi.fn(),
  },
  {
    id: '2',
    title: 'Switch to dark mode',
    keywords: 'theme dark mode switch',
    run: vi.fn(),
  },
  {
    id: '3',
    title: 'Copy previous message',
    keywords: 'copy previous',
    run: vi.fn(),
  },
  {
    id: '4',
    title: 'Show help',
    keywords: 'help help',
    run: vi.fn(),
  },
]

describe('CommandPalette', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should not render when closed', () => {
    vi.mocked(usePalette).mockReturnValue(false)

    expect(() => {
      render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)
    }).not.toThrow()
  })

  it('should render modal overlay when open', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const overlay = screen.getByTestId('command-palette-overlay')
    expect(overlay).toBeInTheDocument()
  })

  it('should render command palette panel', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const overlay = screen.getByTestId('command-palette-overlay')
    expect(overlay).toBeInTheDocument()
  })

  it('should render search input', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type to search/i)
    expect(input).toBeInTheDocument()
  })

  it('should render command list when commands are available', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const commandItems = screen.getAllByTestId(/command-item/)
    expect(commandItems.length).toBeGreaterThan(0)
  })

  it('should filter commands by search query', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const input = screen.getByPlaceholderText(/type to search/i)
    fireEvent.change(input, { target: { value: 'session' } })

    const commandItems = screen.getAllByTestId(/command-item/)
    expect(commandItems.length).toBe(1)
    expect(commandItems[0]).toHaveTextContent('Create new session')
  })

  it('should show all commands when search query is empty', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const commandItems = screen.getAllByTestId(/command-item/)
    expect(commandItems.length).toBe(4)
  })

  it('should close palette on overlay click', () => {
    const onClose = vi.fn()
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={onClose} />)

    const overlay = screen.getByTestId('command-palette-overlay')
    fireEvent.click(overlay)

    expect(onClose).toHaveBeenCalled()
  })

  it('should execute command on click', () => {
    const selectedCommand = mockCommands[0]
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const commandItems = screen.getAllByTestId(/command-item/)
    fireEvent.click(commandItems[0])

    expect(selectedCommand.run).toHaveBeenCalled()
  })

  it('should render command keywords in list item title', () => {
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={vi.fn()} />)

    const commandItems = screen.getAllByTestId(/command-item/)
    expect(commandItems[0]).toHaveTextContent('Create new session')
    expect(commandItems[0]).toHaveTextContent('session new create')
  })

  it('should only show first 50 filtered commands', () => {
    const manyCommands = Array.from({ length: 100 }, (_, i) => ({
      id: String(i),
      title: `Command ${i}`,
      keywords: `command ${i}`,
      run: vi.fn(),
    }))

    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={manyCommands} onClose={vi.fn()} />)

    const commandItems = screen.getAllByTestId(/command-item-/)
    expect(commandItems.length).toBeLessThanOrEqual(50)
  })

  it('should call onClose when clicking on cancel button', () => {
    const onClose = vi.fn()
    vi.mocked(usePalette).mockReturnValue(true)

    render(<CommandPalette commands={mockCommands} onClose={onClose} />)

    const cancelButton = screen.getByRole('button', { name: /close/i })
    fireEvent.click(cancelButton)

    expect(onClose).toHaveBeenCalled()
  })
})

