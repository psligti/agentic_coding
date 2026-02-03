import { useMemo } from 'react'
import { CommandPalette } from './CommandPalette'
import RightDrawer from './RightDrawer'
import { ComposerBar } from './ComposerBar'
import { StatusBar } from './StatusBar'
import { ThemeProvider } from './ThemeProvider'
import { TopBar } from './TopBar'
import { ConversationTimeline } from './ConversationTimeline'
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts'
import { useSetPaletteOpen } from '../store'
import './AppLayout.css'

export function AppLayout() {
  const commands = useMemo(() => [], [])
  const setPaletteOpen = useSetPaletteOpen()

  useKeyboardShortcuts()

  return (
    <ThemeProvider>
      <div className="app-layout">
        <TopBar />
        <ConversationTimeline />
        <ComposerBar />
        <StatusBar />
        <CommandPalette commands={commands} onClose={() => setPaletteOpen(false)} />
        <RightDrawer />
      </div>
    </ThemeProvider>
  )
}
