import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useCurrentSessionThemeId } from '../store/index'

type Mode = 'dark' | 'light'

interface ThemeContextType {
  mode: Mode
  isDark: boolean
  toggleMode: () => void
  denseMode: boolean
  toggleDenseMode: () => void
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [mode, setMode] = useState<Mode>('dark')
  const [denseMode, setDenseMode] = useState(false)
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

    const savedDenseMode = localStorage.getItem('dense-mode') === 'true'
    setDenseMode(savedDenseMode)
  }, [])

  // Apply data-theme attribute for themeId (from session state)
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeId)
  }, [themeId])

  // Apply dense class when denseMode changes
  useEffect(() => {
    if (denseMode) {
      document.documentElement.classList.add('dense')
    } else {
      document.documentElement.classList.remove('dense')
    }
  }, [denseMode])

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

  const toggleDenseMode = () => {
    const newDenseMode = !denseMode
    setDenseMode(newDenseMode)
    localStorage.setItem('dense-mode', String(newDenseMode))
  }

  const isDark = mode === 'dark'

  return (
    <ThemeContext.Provider value={{ mode, isDark, toggleMode, denseMode, toggleDenseMode }}>
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
