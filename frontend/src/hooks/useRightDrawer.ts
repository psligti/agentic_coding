import { useState, useEffect } from 'react'

/**
 * Hook to manage right drawer state with localStorage persistence.
 * Provides open state, setter, and toggle functions.
 */
export function useRightDrawer() {
  const [open, setOpen] = useState(false)

  // Initialize from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('rightDrawerOpen')
    if (saved !== null) {
      setOpen(saved === 'true')
    }
  }, [])

  // Persist state to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('rightDrawerOpen', String(open))
  }, [open])

  const setRightDrawerOpen = (value: boolean) => {
    setOpen(value)
  }

  const toggleRightDrawer = () => {
    setOpen((prev) => !prev)
  }

  return {
    open,
    setRightDrawerOpen,
    toggleRightDrawer,
  }
}
