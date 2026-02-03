import { render } from '@testing-library/react'
import { ConversationTimelineWrapper } from './ConversationTimelineWrapper'

vi.mock('./ConversationTimeline', () => ({
  ConversationTimeline: () => <div>Timeline</div>,
}))

vi.mock('./ComposerBar', () => ({
  ComposerBar: () => <div>Composer</div>,
}))

describe('ConversationTimelineWrapper', () => {
  it('renders timeline and composer', () => {
    const { getByText } = render(<ConversationTimelineWrapper />)
    expect(getByText('Timeline')).toBeInTheDocument()
    expect(getByText('Composer')).toBeInTheDocument()
  })
})
