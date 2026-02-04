import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { useMemoryUsage, useModelStatus, useTokenUsage } from '../store'
import { StatusBar } from './StatusBar'

vi.mock('../store', () => ({
  useMemoryUsage: vi.fn(),
  useModelStatus: vi.fn(),
  useTokenUsage: vi.fn(),
}))

describe('StatusBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render model name with connected status indicator', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    render(<StatusBar />)

    expect(screen.getByText('Agent')).toBeInTheDocument()
  })

  it('should render disconnected status indicator when not connected', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: false })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    render(<StatusBar />)

    expect(screen.getByText('Agent')).toBeInTheDocument()
  })

  it('should render memory usage formatted correctly', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 2097152, total: 8388608 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    render(<StatusBar />)

    const memoryElement = screen.getByText('2.0 GB / 8.0 GB')
    expect(memoryElement).toBeInTheDocument()
    expect(memoryElement.textContent).toBe('2.0 GB / 8.0 GB')
  })

  it('should render token count formatted correctly', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 1500000, limit: 200000 })
    render(<StatusBar />)

    const tokensElement = screen.getByText('1.5M / 200.0K')
    expect(tokensElement).toBeInTheDocument()
    expect(tokensElement.textContent).toBe('1.5M / 200.0K')
  })

  it('should render token count as plain number when less than 1000', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 500, limit: 200000 })
    render(<StatusBar />)

    const tokensElement = screen.getByText('500 / 200.0K')
    expect(tokensElement).toBeInTheDocument()
    expect(tokensElement.textContent).toBe('500 / 200.0K')
  })

  it('should render divider between information', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    render(<StatusBar />)

    const dividers = screen.getAllByText('|')
    expect(dividers).toHaveLength(3)
  })

  it('should render keyboard shortcuts hints', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    render(<StatusBar />)

    expect(screen.getByText('Ctrl+K')).toBeInTheDocument()
    expect(screen.getByText('Ctrl+D')).toBeInTheDocument()
    expect(screen.getByText('Esc')).toBeInTheDocument()
  })

  it('should use provided className', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    const { container } = render(<StatusBar className="test-class" />)

    const statusbar = container.querySelector('div.flex.items-center.justify-between')
    expect(statusbar).toHaveClass('test-class')
  })

  it('should render all elements in correct order', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0, limit: 200000 })
    render(<StatusBar />)

    expect(screen.getByText('Agent')).toBeInTheDocument()
    expect(screen.getByText('●')).toBeInTheDocument()
    expect(screen.getByTitle('Memory usage')).toBeInTheDocument()
    expect(screen.getByTitle('Token usage')).toBeInTheDocument()
    expect(screen.getByText('Ctrl+K')).toBeInTheDocument()
    expect(screen.getByText('Ctrl+D')).toBeInTheDocument()
    expect(screen.getByText('Esc')).toBeInTheDocument()
  })
})
