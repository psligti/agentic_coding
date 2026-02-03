import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../components/ThemeProvider';

// Mock window matchMedia for theme tests
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Helper function to render TestComponent with ThemeProvider
function renderTestComponent() {
  function TestComponent() {
    const { mode, toggleMode, isDark } = useTheme();
    return (
      <div>
        <span data-testid="mode">{mode}</span>
        <span data-testid="is-dark">{isDark ? 'true' : 'false'}</span>
        <button data-testid="toggle" onClick={toggleMode}>Toggle</button>
      </div>
    );
  }

  return render(
    <ThemeProvider>
      <TestComponent />
    </ThemeProvider>
  );
}

describe('ThemeProvider', () => {
  beforeEach(() => {
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('dark');
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.classList.remove('dark');
  });

  it('provides mode context to children', () => {
    renderTestComponent();

    expect(screen.getByTestId('mode')).toHaveTextContent('dark');
  });

  it('toggles mode when toggleMode is called', () => {
    renderTestComponent();

    expect(screen.getByTestId('mode')).toHaveTextContent('dark');

    fireEvent.click(screen.getByTestId('toggle'));
    expect(screen.getByTestId('mode')).toHaveTextContent('light');
  });

  it('provides mode state to context consumers', () => {
    renderTestComponent();

    expect(screen.getByTestId('mode')).toHaveTextContent('dark');
    expect(screen.getByTestId('is-dark')).toHaveTextContent('true');
  });

  it('toggles mode when toggleMode is called', () => {
    const { unmount } = renderTestComponent();

    expect(screen.getByTestId('mode')).toHaveTextContent('dark');

    fireEvent.click(screen.getByTestId('toggle'));
    expect(screen.getByTestId('mode')).toHaveTextContent('light');
    unmount();
  });

  it('applies .dark class to document.documentElement by default', () => {
    render(
      <ThemeProvider>
        <div>Test</div>
      </ThemeProvider>
    );

    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });

  it('removes .dark class when mode is light', () => {
    renderTestComponent();

    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(screen.getByTestId('mode')).toHaveTextContent('dark');

    fireEvent.click(screen.getByTestId('toggle'));
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(screen.getByTestId('mode')).toHaveTextContent('light');
  });

  it('applies data-theme="aurora" by default (when no session)', () => {
    render(
      <ThemeProvider>
        <div>Test</div>
      </ThemeProvider>
    );

    expect(document.documentElement.getAttribute('data-theme')).toBe('aurora');
  });

  it('preserves mode preference in localStorage', () => {
    const { unmount } = renderTestComponent();

    fireEvent.click(screen.getByTestId('toggle'));
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(localStorage.getItem('theme-mode')).toBe('light');

    unmount();

    renderTestComponent();
    expect(document.documentElement.classList.contains('dark')).toBe(false);
    expect(screen.getByTestId('mode')).toHaveTextContent('light');
  });

  it('throws error when useTheme is used outside ThemeProvider', () => {
    function TestComponent() {
      useTheme();
      return null;
    }

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useTheme must be used within a ThemeProvider');
  });
});
