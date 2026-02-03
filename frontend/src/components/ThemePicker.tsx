import { useState } from 'react'
import { useCurrentSession } from '../store'
import { useSessions } from '../hooks/useSessions'

type ThemeId = 'aurora' | 'ocean' | 'ember'

interface ThemeOption {
  id: ThemeId
  name: string
  description: string
  gradient: string
}

const themeOptions: ThemeOption[] = [
  {
    id: 'aurora',
    name: 'Aurora',
    description: 'Purple and indigo gradients',
    gradient: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
  },
  {
    id: 'ocean',
    name: 'Ocean',
    description: 'Teal and cyan depths',
    gradient: 'linear-gradient(135deg, #14b8a6 0%, #06b6d4 100%)',
  },
  {
    id: 'ember',
    name: 'Ember',
    description: 'Warm amber and orange glow',
    gradient: 'linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)',
  },
]

export default function ThemePicker() {
  const currentSession = useCurrentSession()
  const { updateSession } = useSessions()
  const [updating, setUpdating] = useState<ThemeId | null>(null)
  const currentThemeId = (currentSession?.theme_id as ThemeId) || 'aurora'

  const handleThemeSelect = async (themeId: ThemeId) => {
    if (!currentSession || themeId === currentThemeId || updating) {
      return
    }

    setUpdating(themeId)

    try {
      await updateSession(currentSession.id, { theme_id: themeId })
    } catch (error) {
      console.error('Failed to update theme:', error)
    } finally {
      setUpdating(null)
    }
  }

  return (
    <div className="theme-picker">
      <div className="theme-picker__label">Theme Preset</div>
      <div className="theme-picker__options" role="radiogroup" aria-label="Select theme">
        {themeOptions.map((option) => {
          const isActive = option.id === currentThemeId
          const isUpdating = updating === option.id

          return (
            <button
              key={option.id}
              className={`theme-picker__option ${isActive ? 'is-active' : ''}`}
              onClick={() => handleThemeSelect(option.id)}
              disabled={!!updating}
              role="radio"
              aria-checked={isActive}
              aria-label={`Select ${option.name} theme`}
              title={option.description}
            >
              <div className="theme-picker__swatch" style={{ background: option.gradient }} />
              <div className="theme-picker__info">
                <span className="theme-picker__name">{option.name}</span>
                <span className="theme-picker__description">{option.description}</span>
              </div>
              {isUpdating && (
                <span className="theme-picker__updating">Updating...</span>
              )}
              {isActive && !isUpdating && (
                <span className="theme-picker__active" aria-label="Active theme">✓</span>
              )}
            </button>
          )
        })}
      </div>
      {!currentSession && (
        <div className="theme-picker__note">Create a session to change themes</div>
      )}
    </div>
  )
}
