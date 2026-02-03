import { ConversationTimeline } from './ConversationTimeline'
import { ComposerBar } from './ComposerBar'

export function ConversationTimelineWrapper() {
  return (
    <div className="app-layout">
      <ConversationTimeline />
      <ComposerBar />
    </div>
  )
}
