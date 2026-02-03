import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useCurrentSessionThemeId } from '../store/index'

type Mode = 'dark' | 'light'

interface ThemeContextType {
  mode: Mode
  isDark: boolean
  toggleMode: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [mode, setMode] = useState<Mode>('dark')
  const themeId = useCurrentSessionThemeId() || 'aurora'

  useEffect(() => {
    document.documentElement.classList.add('dark')

    const savedMode = localStorage.getItem('theme-mode') as Mode | null
    if (savedMode) {
      setMode(savedMode)
      if (savedMode === 'light') {
        document.documentElement.classList.remove('dark')
      } else {
        document.documentElement.classList.add('dark')
      }
    }
  }, [])

  // Apply data-theme attribute for themeId (from session state)
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeId)
  }, [themeId])

  const toggleMode = () => {
    const newMode: Mode = mode === 'dark' ? 'light' : 'dark'
    setMode(newMode)
    if (newMode === 'light') {
      document.documentElement.classList.remove('dark')
    } else {
      document.documentElement.classList.add('dark')
    }
    localStorage.setItem('theme-mode', newMode)
  }

  const isDark = mode === 'dark'

  return (
    <ThemeContext.Provider value={{ mode, isDark, toggleMode }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme() {
  const context = useContext(ThemeContext)

  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }

  return context
}
