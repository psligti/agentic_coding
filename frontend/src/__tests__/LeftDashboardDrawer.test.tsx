import { render, screen, fireEvent } from '@testing-library/react'
import LeftDashboardDrawer from '../components/LeftDashboardDrawer'
import { describe, it, vi, beforeEach, expect } from 'vitest'

// Mock store hooks
const mockSetLeftDashboardOpen = vi.fn()
const mockSetLeftDashboardPinned = vi.fn()
const mockSetDrawerOpen = vi.fn()

let mockLeftDashboardState = { open: false, pinned: false }
let mockDrawerState = { open: false }
let mockTelemetry: any = {
  git: { is_repo: false, branch: '', dirty_count: 0, staged_count: 0 },
  tools: { running: null, last: null },
  effort: { effort_score: 0 },
}

vi.mock('../store', () => ({
  useLeftDashboard: () => mockLeftDashboardState,
  useSetLeftDashboardOpen: () => mockSetLeftDashboardOpen,
  useSetLeftDashboardPinned: () => mockSetLeftDashboardPinned,
  useTelemetry: () => mockTelemetry,
  useDrawer: () => mockDrawerState,
  useSetDrawerOpen: () => mockSetDrawerOpen,
}))

describe('LeftDashboardDrawer', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockLeftDashboardState = { open: false, pinned: false }
    mockDrawerState = { open: false }
    mockTelemetry = {
      git: { is_repo: false, branch: '', dirty_count: 0, staged_count: 0 },
      tools: { running: null, last: null },
      effort: { effort_score: 0 },
    }
    // Mock window.matchMedia for narrow screen detection
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1200, // Default to wide screen
    })
  })

  describe('Open/Close Toggle', () => {
    it('does not render when open is false and not pinned', () => {
      mockLeftDashboardState = { open: false, pinned: false }
      const { container } = render(<LeftDashboardDrawer />)
      expect(container.firstChild).toBeNull()
    })

    it('renders when open is true', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByTestId('left-dashboard')).toBeInTheDocument()
    })

    it('renders when pinned is true even if open is false (wide screen)', () => {
      mockLeftDashboardState = { open: false, pinned: true }
      render(<LeftDashboardDrawer />)
      expect(screen.getByTestId('left-dashboard')).toBeInTheDocument()
    })

    it('does not render when pinned is true but on narrow screen and open is false', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 500, // Narrow screen
      })
      mockLeftDashboardState = { open: false, pinned: true }
      const { container } = render(<LeftDashboardDrawer />)
      expect(container.firstChild).toBeNull()
    })

    it('calls setLeftDashboardOpen(false) when close button is clicked', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      const closeButton = screen.getByTestId('left-dashboard-close')
      fireEvent.click(closeButton)
      expect(mockSetLeftDashboardOpen).toHaveBeenCalledWith(false)
    })

    it('calls setLeftDashboardOpen(false) when Escape key is pressed', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      fireEvent.keyDown(window, { key: 'Escape' })
      expect(mockSetLeftDashboardOpen).toHaveBeenCalledWith(false)
    })
  })

  describe('Pin/Unpin Toggle', () => {
    it('renders pin button on wide screens', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByTestId('left-dashboard-pin')).toBeInTheDocument()
    })

    it('does not render pin button on narrow screens', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        value: 500, // Narrow screen
      })
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.queryByTestId('left-dashboard-pin')).not.toBeInTheDocument()
    })

    it('shows 📍 icon when not pinned', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      const pinButton = screen.getByTestId('left-dashboard-pin')
      expect(pinButton).toHaveTextContent('📍')
    })

    it('shows 📌 icon when pinned', () => {
      mockLeftDashboardState = { open: true, pinned: true }
      render(<LeftDashboardDrawer />)
      const pinButton = screen.getByTestId('left-dashboard-pin')
      expect(pinButton).toHaveTextContent('📌')
    })

    it('calls setLeftDashboardPinned(true) when pin button is clicked (unpinned -> pinned)', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      const pinButton = screen.getByTestId('left-dashboard-pin')
      fireEvent.click(pinButton)
      expect(mockSetLeftDashboardPinned).toHaveBeenCalledWith(true)
    })

    it('calls setLeftDashboardPinned(false) when pin button is clicked (pinned -> unpinned)', () => {
      mockLeftDashboardState = { open: true, pinned: true }
      render(<LeftDashboardDrawer />)
      const pinButton = screen.getByTestId('left-dashboard-pin')
      fireEvent.click(pinButton)
      expect(mockSetLeftDashboardPinned).toHaveBeenCalledWith(false)
    })
  })

  describe('Pinned Drawer Behavior', () => {
    it('stays open when clicking overlay if pinned (wide screen)', () => {
      mockLeftDashboardState = { open: true, pinned: true }
      render(<LeftDashboardDrawer />)
      const dashboard = screen.getByTestId('left-dashboard').parentElement
      // Simulate clicking on the overlay (not on the drawer content)
      if (dashboard && dashboard.parentElement) {
        fireEvent.click(dashboard.parentElement)
      }
      // Should NOT call setLeftDashboardOpen because it's pinned
      expect(mockSetLeftDashboardOpen).not.toHaveBeenCalled()
    })

    it('closes when clicking overlay if not pinned (overlay mode)', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      const dashboard = screen.getByTestId('left-dashboard').parentElement
      // Simulate clicking on the overlay
      if (dashboard && dashboard.parentElement) {
        fireEvent.click(dashboard.parentElement)
      }
      // Should call setLeftDashboardOpen(false) because it's not pinned
      expect(mockSetLeftDashboardOpen).toHaveBeenCalledWith(false)
    })

    it('does not call setLeftDashboardOpen when clicking inside drawer content', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      const dashboard = screen.getByTestId('left-dashboard')
      // Click inside the drawer
      fireEvent.click(dashboard)
      expect(mockSetLeftDashboardOpen).not.toHaveBeenCalled()
    })
  })

  describe('Drawer Content', () => {
    it('displays "Now" header', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('Now')).toBeInTheDocument()
    })

    it('displays git branch when available', () => {
      mockTelemetry.git = { is_repo: true, branch: 'main', dirty_count: 0, staged_count: 0 }
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('main')).toBeInTheDocument()
    })

    it('displays dirty count when available', () => {
      mockTelemetry.git = { is_repo: true, branch: 'main', dirty_count: 3, staged_count: 0 }
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('+3')).toBeInTheDocument()
    })

    it('displays staged count when available', () => {
      mockTelemetry.git = { is_repo: true, branch: 'main', dirty_count: 0, staged_count: 2 }
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('*2')).toBeInTheDocument()
    })

    it('displays running tool when available', () => {
      mockTelemetry.tools = { running: { tool_id: 'bash', since: Date.now() }, last: undefined }
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('bash')).toBeInTheDocument()
    })

    it('displays last tool when no running tool', () => {
      mockTelemetry.tools = { running: undefined, last: { tool_id: 'read', status: 'completed' } }
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('read')).toBeInTheDocument()
    })

    it('displays effort emoji based on score', () => {
      mockTelemetry.effort = { effort_score: 3 }
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('🧠⚡')).toBeInTheDocument()
    })

    it('displays quick actions', () => {
      mockLeftDashboardState = { open: true, pinned: false }
      render(<LeftDashboardDrawer />)
      expect(screen.getByText('Toggle dashboard')).toBeInTheDocument()
      expect(screen.getByText('Command palette')).toBeInTheDocument()
      expect(screen.getByText('Settings')).toBeInTheDocument()
    })
  })
})
