import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { useMemoryUsage, useModelStatus, useTokenUsage, useTelemetry } from '../store'
import { StatusBar } from './StatusBar'

vi.mock('../store', () => ({
  useMemoryUsage: vi.fn(),
  useModelStatus: vi.fn(),
  useTokenUsage: vi.fn(),
  useTelemetry: vi.fn(),
}))

describe('StatusBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: {},
    })
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
    expect(dividers).toHaveLength(6)
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
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    expect(screen.getByText('Agent')).toBeInTheDocument()
    expect(screen.getByText('●')).toBeInTheDocument()
    expect(screen.getByTitle('Memory usage')).toBeInTheDocument()
    expect(screen.getByTitle('Token usage')).toBeInTheDocument()
    expect(screen.getByText('Ctrl+K')).toBeInTheDocument()
    expect(screen.getByText('Ctrl+D')).toBeInTheDocument()
    expect(screen.getByText('Esc')).toBeInTheDocument()
  })

  it('should render git indicator with dash when not a repo', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const gitIndicator = screen.getByTestId('status-git')
    expect(gitIndicator.textContent).toBe('—')
  })

  it('should render git indicator with branch name only', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: true, branch: 'main' },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const gitIndicator = screen.getByTestId('status-git')
    expect(gitIndicator.textContent).toBe('main')
  })

  it('should render git indicator with dirty count', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: true, branch: 'main', dirty_count: 3 },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const gitIndicator = screen.getByTestId('status-git')
    expect(gitIndicator.textContent).toBe('main +3')
  })

  it('should render git indicator with ahead/behind counts', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: true, branch: 'main', ahead: 2, behind: 1 },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const gitIndicator = screen.getByTestId('status-git')
    expect(gitIndicator.textContent).toBe('main ↑2 ↓1')
  })

  it('should render git indicator with all values', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: true, branch: 'feature', dirty_count: 5, ahead: 3, behind: 2 },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const gitIndicator = screen.getByTestId('status-git')
    expect(gitIndicator.textContent).toBe('feature +5 ↑3 ↓2')
  })

  it('should render tools indicator with dash when no tools', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const toolsIndicator = screen.getByTestId('status-tools')
    expect(toolsIndicator.textContent).toBe('—')
  })

  it('should render tools indicator with running tool', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: { running: { tool_id: 'bash', since: Date.now() } },
      effort: {},
    })
    render(<StatusBar />)

    const toolsIndicator = screen.getByTestId('status-tools')
    expect(toolsIndicator.textContent).toBe('↻ bash')
  })

  it('should render tools indicator with last completed tool', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: { last: { tool_id: 'grep', status: 'completed' } },
      effort: {},
    })
    render(<StatusBar />)

    const toolsIndicator = screen.getByTestId('status-tools')
    expect(toolsIndicator.textContent).toBe('grep')
  })

  it('should render tools indicator with failure badge', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: { last: { tool_id: 'bash', status: 'failed' }, error_count: 2 },
      effort: {},
    })
    render(<StatusBar />)

    const toolsIndicator = screen.getByTestId('status-tools')
    expect(toolsIndicator.textContent).toBe('bash (2⚠)')
  })

  it('should render effort indicator with default emoji when score undefined', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: {},
    })
    render(<StatusBar />)

    const effortIndicator = screen.getByTestId('status-effort')
    expect(effortIndicator.textContent).toBe('🤓')
  })

  it('should render effort indicator with emoji for score 0', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: { effort_score: 0 },
    })
    render(<StatusBar />)

    const effortIndicator = screen.getByTestId('status-effort')
    expect(effortIndicator.textContent).toBe('🤓')
  })

  it('should render effort indicator with emoji for score 3', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: { effort_score: 3 },
    })
    render(<StatusBar />)

    const effortIndicator = screen.getByTestId('status-effort')
    expect(effortIndicator.textContent).toBe('🧠⚡')
  })

  it('should render effort indicator with emoji for score 5', () => {
    vi.mocked(useMemoryUsage).mockReturnValue({ used: 0, total: 8 })
    vi.mocked(useModelStatus).mockReturnValue({ name: 'Agent', connected: true })
    vi.mocked(useTokenUsage).mockReturnValue({ input: 0, output: 0, total: 0 })
    vi.mocked(useTelemetry).mockReturnValue({
      git: { is_repo: false },
      tools: {},
      effort: { effort_score: 5 },
    })
    render(<StatusBar />)

    const effortIndicator = screen.getByTestId('status-effort')
    expect(effortIndicator.textContent).toBe('🧠💥')
  })
})
