import { render, screen, fireEvent } from '@testing-library/react'
import RightDrawer from './RightDrawer'

const mockSetDrawerTab = vi.fn()
const mockSetDrawerOpen = vi.fn()
const mockSetTheme = vi.fn()

vi.mock('../hooks/useSessions', () => ({
  useSessions: () => ({
    createSession: vi.fn(),
    deleteSession: vi.fn(),
  }),
}))

vi.mock('../hooks/useAccounts', () => ({
  useAccounts: () => ({
    createAccount: vi.fn(),
    deleteAccount: vi.fn(),
    setDefaultAccount: vi.fn(),
  }),
}))

vi.mock('../store', () => ({
  useStore: (selector: any) => selector({
    drawerOpen: true,
    drawerTab: 'sessions',
    sessions: [
      { id: '1', title: 'Session 1', time_created: 0, time_updated: 0, message_count: 0 },
    ],
    theme: 'dark',
    setTheme: mockSetTheme,
    setDrawerTab: mockSetDrawerTab,
    setDrawerOpen: mockSetDrawerOpen,
  }),
  useCurrentSession: () => null,
  useSetCurrentSession: () => vi.fn(),
  useSetDrawerTab: () => mockSetDrawerTab,
  useSetDrawerOpen: () => mockSetDrawerOpen,
  useAgentsState: () => [],
  useModelsState: () => [],
  useSkillsState: () => [],
  useToolsState: () => [],
  useAccountsState: () => [],
  useSelectedAgent: () => null,
  useSelectedModel: () => null,
  useSelectedSkills: () => [],
  useSelectedAccount: () => null,
  useSetSelectedAgent: () => vi.fn(),
  useSetSelectedModel: () => vi.fn(),
  useSetSelectedSkills: () => vi.fn(),
  useSetSelectedAccount: () => vi.fn(),
}))

describe('RightDrawer', () => {
  it('renders tabs for all sections', () => {
    render(<RightDrawer />)
    const tabs = screen.getAllByRole('tab')
    expect(tabs).toHaveLength(8)
    expect(screen.getByRole('tab', { name: 'Sessions' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Agents' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Models' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Skills' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Tools' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Accounts' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Settings' })).toBeInTheDocument()
    expect(screen.getByRole('tab', { name: 'Info' })).toBeInTheDocument()
  })

  it('renders sessions list', () => {
    render(<RightDrawer />)
    expect(screen.getByText('Session 1')).toBeInTheDocument()
  })

  it('switches to Agents tab when clicked', () => {
    render(<RightDrawer />)
    const agentsTab = screen.getByRole('tab', { name: 'Agents' })
    fireEvent.click(agentsTab)
    expect(mockSetDrawerTab).toHaveBeenCalledWith('agents')
  })
})
