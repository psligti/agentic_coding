import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CommandPalette, type Command } from '../components/CommandPalette'

vi.mock('../store', () => ({
  usePalette: () => true,
  useSetPaletteOpen: () => vi.fn(),
}))

vi.mock('react-dom', () => ({
  createPortal: (children: React.ReactNode) => children,
}))

describe('CommandPalette Command Execution', () => {
  let mockCommands: Command[]
  let mockOnClose: ReturnType<typeof vi.fn>

  beforeEach(() => {
    mockOnClose = vi.fn()
    mockCommands = [
      {
        id: 'toggle-dense-mode',
        title: 'Enable Dense Mode',
        keywords: 'dense mode compact spacing layout',
        run: vi.fn(),
      },
      {
        id: 'theme-graphite',
        title: 'Theme: Graphite',
        keywords: 'theme graphite industrial',
        run: vi.fn(),
      },
      {
        id: 'toggle-left-dashboard',
        title: 'Open Left Dashboard',
        keywords: 'left dashboard sidebar panel toggle',
        run: vi.fn(),
      },
      {
        id: 'pin-left-dashboard',
        title: 'Pin Left Dashboard',
        keywords: 'left dashboard sidebar panel pin unpin',
        run: vi.fn(),
      },
      {
        id: 'open-drawer-tools',
        title: 'Open Tools Drawer',
        keywords: 'drawer right tools panel',
        run: vi.fn(),
      },
      {
        id: 'open-drawer-sessions',
        title: 'Open Sessions Drawer',
        keywords: 'drawer right sessions panel',
        run: vi.fn(),
      },
      {
        id: 'open-drawer-agents',
        title: 'Open Agents Drawer',
        keywords: 'drawer right agents panel',
        run: vi.fn(),
      },
      {
        id: 'refresh-telemetry',
        title: 'Refresh Telemetry',
        keywords: 'telemetry refresh update snapshot',
        run: vi.fn(),
      },
    ]
  })

  describe('Command Registry Stability', () => {
    it('receives commands prop correctly', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByTestId('command-item-toggle-dense-mode')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-theme-graphite')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-toggle-left-dashboard')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-pin-left-dashboard')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-open-drawer-tools')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-open-drawer-sessions')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-open-drawer-agents')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-refresh-telemetry')).toBeInTheDocument()
    })

    it('displays all expected commands', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByText('Enable Dense Mode')).toBeInTheDocument()
      expect(screen.getByText('Theme: Graphite')).toBeInTheDocument()
      expect(screen.getByText('Open Left Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Pin Left Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Open Tools Drawer')).toBeInTheDocument()
      expect(screen.getByText('Open Sessions Drawer')).toBeInTheDocument()
      expect(screen.getByText('Open Agents Drawer')).toBeInTheDocument()
      expect(screen.getByText('Refresh Telemetry')).toBeInTheDocument()
    })

    it('has correct count of commands', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      const commandItems = screen.getAllByTestId(/command-item-/)
      expect(commandItems).toHaveLength(8)
    })
  })

  describe('Command Labels and Keybindings', () => {
    it('displays correct labels for toggle commands', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByText('Enable Dense Mode')).toBeInTheDocument()
      expect(screen.getByText('Open Left Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Pin Left Dashboard')).toBeInTheDocument()
    })

    it('displays correct labels for drawer commands', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByText('Open Tools Drawer')).toBeInTheDocument()
      expect(screen.getByText('Open Sessions Drawer')).toBeInTheDocument()
      expect(screen.getByText('Open Agents Drawer')).toBeInTheDocument()
    })

    it('displays correct labels for theme and telemetry commands', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByText('Theme: Graphite')).toBeInTheDocument()
      expect(screen.getByText('Refresh Telemetry')).toBeInTheDocument()
    })

    it('displays keywords for searchability', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByText('dense mode compact spacing layout')).toBeInTheDocument()
      expect(screen.getByText('theme graphite industrial')).toBeInTheDocument()
      expect(screen.getByText('left dashboard sidebar panel toggle')).toBeInTheDocument()
      expect(screen.getByText('left dashboard sidebar panel pin unpin')).toBeInTheDocument()
      expect(screen.getByText('drawer right tools panel')).toBeInTheDocument()
      expect(screen.getByText('drawer right sessions panel')).toBeInTheDocument()
      expect(screen.getByText('drawer right agents panel')).toBeInTheDocument()
      expect(screen.getByText('telemetry refresh update snapshot')).toBeInTheDocument()
    })
  })

  describe('Command Execution', () => {
    it('executes toggle-dense-mode command when clicked', () => {
      const toggleDenseMode = vi.fn()
      mockCommands[0].run = toggleDenseMode

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-toggle-dense-mode'))

      expect(toggleDenseMode).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes theme-graphite command when clicked', () => {
      const setGraphiteTheme = vi.fn()
      mockCommands[1].run = setGraphiteTheme

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-theme-graphite'))

      expect(setGraphiteTheme).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes toggle-left-dashboard command when clicked', () => {
      const toggleLeftDashboard = vi.fn()
      mockCommands[2].run = toggleLeftDashboard

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-toggle-left-dashboard'))

      expect(toggleLeftDashboard).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes pin-left-dashboard command when clicked', () => {
      const toggleLeftDashboardPinned = vi.fn()
      mockCommands[3].run = toggleLeftDashboardPinned

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-pin-left-dashboard'))

      expect(toggleLeftDashboardPinned).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes open-drawer-tools command when clicked', () => {
      const openToolsDrawer = vi.fn()
      mockCommands[4].run = openToolsDrawer

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-open-drawer-tools'))

      expect(openToolsDrawer).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes open-drawer-sessions command when clicked', () => {
      const openSessionsDrawer = vi.fn()
      mockCommands[5].run = openSessionsDrawer

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-open-drawer-sessions'))

      expect(openSessionsDrawer).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes open-drawer-agents command when clicked', () => {
      const openAgentsDrawer = vi.fn()
      mockCommands[6].run = openAgentsDrawer

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-open-drawer-agents'))

      expect(openAgentsDrawer).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('executes refresh-telemetry command when clicked', () => {
      const refreshTelemetry = vi.fn()
      mockCommands[7].run = refreshTelemetry

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-refresh-telemetry'))

      expect(refreshTelemetry).toHaveBeenCalledTimes(1)
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })

    it('closes palette after executing any command', () => {
      const mockRun = vi.fn()
      mockCommands.forEach(cmd => cmd.run = mockRun)

      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      fireEvent.click(screen.getByTestId('command-item-toggle-dense-mode'))
      expect(mockOnClose).toHaveBeenCalledTimes(1)

      fireEvent.click(screen.getByTestId('command-item-theme-graphite'))
      expect(mockOnClose).toHaveBeenCalledTimes(2)
    })
  })

  describe('Command Filtering', () => {
    it('filters commands by title', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      const input = screen.getByPlaceholderText('Type to search…')
      fireEvent.change(input, { target: { value: 'dense' } })

      expect(screen.getByText('Enable Dense Mode')).toBeInTheDocument()
      expect(screen.queryByText('Theme: Graphite')).not.toBeInTheDocument()
      expect(screen.queryByText('Open Left Dashboard')).not.toBeInTheDocument()
    })

    it('filters commands by keywords', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      const input = screen.getByPlaceholderText('Type to search…')
      fireEvent.change(input, { target: { value: 'drawer' } })

      expect(screen.getByText('Open Tools Drawer')).toBeInTheDocument()
      expect(screen.getByText('Open Sessions Drawer')).toBeInTheDocument()
      expect(screen.getByText('Open Agents Drawer')).toBeInTheDocument()
      expect(screen.queryByText('Open Left Dashboard')).not.toBeInTheDocument()
      expect(screen.queryByText('Pin Left Dashboard')).not.toBeInTheDocument()
      expect(screen.queryByText('Enable Dense Mode')).not.toBeInTheDocument()
    })

    it('shows all commands when query is empty', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      const input = screen.getByPlaceholderText('Type to search…')
      fireEvent.change(input, { target: { value: 'dense' } })
      expect(screen.getAllByTestId(/command-item-/)).toHaveLength(1)

      fireEvent.change(input, { target: { value: '' } })
      expect(screen.getAllByTestId(/command-item-/)).toHaveLength(8)
    })

    it('shows "No commands found" when no matches', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      const input = screen.getByPlaceholderText('Type to search…')
      fireEvent.change(input, { target: { value: 'nonexistent' } })

      expect(screen.getByText('No commands found')).toBeInTheDocument()
    })
  })

  describe('Command Metadata', () => {
    it('commands have correct id values', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      expect(screen.getByTestId('command-item-toggle-dense-mode')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-theme-graphite')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-toggle-left-dashboard')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-pin-left-dashboard')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-open-drawer-tools')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-open-drawer-sessions')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-open-drawer-agents')).toBeInTheDocument()
      expect(screen.getByTestId('command-item-refresh-telemetry')).toBeInTheDocument()
    })

    it('commands have correct title and keywords structure', () => {
      render(<CommandPalette commands={mockCommands} onClose={mockOnClose} />)

      const commandItem = screen.getByTestId('command-item-toggle-dense-mode')
      expect(commandItem).toHaveTextContent('Enable Dense Mode')
      expect(commandItem).toHaveTextContent('dense mode compact spacing layout')
    })

    it('commands have proper run functions', () => {
      mockCommands.forEach(cmd => {
        expect(cmd.run).toBeDefined()
        expect(typeof cmd.run).toBe('function')
      })
    })
  })

  describe('Empty Command Registry', () => {
    it('shows "No commands found" when no commands', () => {
      render(<CommandPalette commands={[]} onClose={mockOnClose} />)

      expect(screen.getByText('No commands found')).toBeInTheDocument()
    })
  })
})
