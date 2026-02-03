import { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { usePalette } from '../store'
import './CommandPalette.css'

export interface Command {
  id: string
  title: string
  keywords: string
  run: () => void
}

interface CommandPaletteProps {
  commands: Command[]
  onClose: () => void
}

export function CommandPalette({ commands, onClose }: CommandPaletteProps) {
  const isOpen = usePalette()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const listRef = useRef<HTMLDivElement>(null)

  const filteredCommands = useMemo(() => {
    const lowerQuery = query.toLowerCase()
    if (!query.trim()) return commands

    return commands.filter((cmd) => {
      return (
        cmd.title.toLowerCase().includes(lowerQuery) ||
        cmd.keywords.toLowerCase().includes(lowerQuery)
      )
    })
  }, [commands, query])

  useEffect(() => {
    setSelectedIndex(0)
  }, [filteredCommands])

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus()
    }
  }, [isOpen])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'Escape') {
        e.preventDefault()
        onClose()
        return
      }

      if (e.key === 'Enter') {
        e.preventDefault()
        const selected = filteredCommands[selectedIndex]
        if (selected) {
          selected.run()
          onClose()
        }
        return
      }

      if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown'].includes(e.key)) {
        e.preventDefault()
        const maxIndex = filteredCommands.length - 1

        if (e.key === 'ArrowUp' || e.key === 'PageUp') {
          setSelectedIndex((prev) => (prev > 0 ? prev - 1 : prev))
        } else if (e.key === 'ArrowDown' || e.key === 'PageDown') {
          setSelectedIndex((prev) => (prev < maxIndex ? prev + 1 : prev))
        }
        return
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex, onClose])

  if (!isOpen) return null

  return createPortal(
    <div
      className="command-palette-overlay"
      onClick={onClose}
      data-testid="command-palette-overlay"
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          onClose()
        }
      }}
    >
      <div className="command-palette" onClick={(e) => e.stopPropagation()}>
        <div className="command-palette__header">
          <div className="command-palette__title">Commands</div>
          <button
            className="command-palette__close"
            onClick={onClose}
            aria-label="Close command palette"
          >
            ✕
          </button>
        </div>

        <input
          ref={inputRef}
          type="text"
          className="command-palette__input"
          placeholder="Type to search…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              onClose()
            }
          }}
        />

        <div className="command-palette__list" ref={listRef}>
          {filteredCommands.slice(0, 50).map((command, index) => (
            <button
              key={command.id}
              className={`command-palette__item ${index === selectedIndex ? 'command-palette__item--selected' : ''}`}
              onClick={() => {
                command.run()
                onClose()
              }}
              onMouseEnter={() => setSelectedIndex(index)}
              data-testid={`command-item-${command.id}`}
            >
              <span className="command-palette__item-title">{command.title}</span>
              <span className="command-palette__item-keywords">{command.keywords}</span>
            </button>
          ))}

          {filteredCommands.length === 0 && (
            <div className="command-palette__empty">No commands found</div>
          )}
        </div>
      </div>
    </div>,
    document.body
  )
}
