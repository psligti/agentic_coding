import { useEffect, useMemo, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { usePalette } from '../store'

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
      className="fixed inset-0 flex items-center justify-center bg-black/45 z-[1000]"
      onClick={onClose}
      data-testid="command-palette-overlay"
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          onClose()
        }
      }}
    >
      <div className="w-[min(900px,92vw)] max-h-[70vh] bg-surface-panel border border-normal rounded-[14px] flex flex-col overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between p-3 border-b border-normal">
          <div className="text-primary font-semibold text-sm">Commands</div>
          <button
            className="bg-transparent border border-normal rounded-[14px] text-primary cursor-pointer px-2 py-1 text-base hover:bg-surface-raised"
            onClick={onClose}
            aria-label="Close command palette"
          >
            ✕
          </button>
        </div>

        <input
          ref={inputRef}
          type="text"
          className="w-full p-3 bg-surface-panel border border-normal rounded-[14px] text-primary text-sm outline-none focus:border-focus focus:ring-2 focus:ring-cyan-500/20"
          placeholder="Type to search…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              onClose()
            }
          }}
        />

        <div className="flex-1 overflow-y-auto p-2 flex flex-col gap-2" ref={listRef}>
          {filteredCommands.slice(0, 50).map((command, index) => (
            <button
              key={command.id}
              className={`flex flex-col w-full p-3 bg-surface-raised border border-normal rounded-[14px] text-primary text-left cursor-pointer transition-colors duration-150 hover:border-focus ${index === selectedIndex ? 'border-focus shadow-[0_0_0_2px_rgba(32,197,255,0.2)]' : ''}`}
              onClick={() => {
                command.run()
                onClose()
              }}
              onMouseEnter={() => setSelectedIndex(index)}
              data-testid={`command-item-${command.id}`}
            >
              <span className="font-semibold text-sm mb-0.5">{command.title}</span>
              <span className="text-xs text-secondary">{command.keywords}</span>
            </button>
          ))}

          {filteredCommands.length === 0 && (
            <div className="p-3 text-secondary text-center text-sm">No commands found</div>
          )}
        </div>
      </div>
    </div>,
    document.body
  )
}
