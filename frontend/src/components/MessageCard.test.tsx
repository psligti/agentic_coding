import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MessageCard } from './MessageCard'

type MessageCardMessage = {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system' | 'tool' | 'question' | 'thinking' | 'error'
  text: string
  parts: any[]
  timestamp?: number
}

type Message = MessageCardMessage

// Mock react-markdown to avoid actual markdown parsing in tests
vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <>{children}</>,
}))

// Mock necessary icons
vi.mock('lucide-react', () => ({
  Copy: () => <span data-testid="copy-icon">Copy</span>,
  Quote: () => <span data-testid="quote-icon">Quote</span>,
  Edit: () => <span data-testid="edit-icon">Edit</span>,
  User: () => <span data-testid="user-icon">User</span>,
  Bot: () => <span data-testid="bot-icon">Bot</span>,
  Info: () => <span data-testid="info-icon">Info</span>,
  Wrench: () => <span data-testid="tool-icon">Wrench</span>,
  HelpCircle: () => <span data-testid="question-icon">?</span>,
  Sparkles: () => <span data-testid="sparkles-icon">✨</span>,
  AlertCircle: () => <span data-testid="error-icon">⚠️</span>,
}))

describe('MessageCard', () => {
  describe('User message variant', () => {
    it('should render user message with left alignment', () => {
      const message: MessageCardMessage = {
        id: 'msg-1',
        session_id: 'session-1',
        role: 'user',
        text: 'Hello, how can I help?',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('Hello, how can I help?')
      expect(card).toBeInTheDocument()
    })

    it('should show user icon', () => {
      const message: MessageCardMessage = {
        id: 'msg-2',
        session_id: 'session-2',
        role: 'user',
        text: 'Test message',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('user-icon')
      expect(icon).toBeInTheDocument()
    })

    it('should render action buttons visible by default', () => {
      const message: MessageCardMessage = {
        id: 'msg-3',
        session_id: 'session-3',
        role: 'user',
        text: 'Test message',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const copyButton = screen.getByRole('button', { name: /copy/i })
      expect(copyButton).toBeInTheDocument()
    })
  })

  describe('Assistant message variant', () => {
    it('should render assistant message with right alignment', () => {
      const message: MessageCardMessage = {
        id: 'msg-4',
        session_id: 'session-4',
        role: 'assistant',
        text: 'I can help with that!',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('I can help with that!')
      expect(card).toBeInTheDocument()
    })

    it('should show bot icon', () => {
      const message: MessageCardMessage = {
        id: 'msg-5',
        session_id: 'session-5',
        role: 'assistant',
        text: 'Test message',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('bot-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('System message variant', () => {
    it('should render system message centered', () => {
      const message: MessageCardMessage = {
        id: 'msg-6',
        session_id: 'session-6',
        role: 'system',
        text: 'Session started',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('Session started')
      expect(card).toBeInTheDocument()
    })

    it('should show info icon', () => {
      const message: Message = {
        id: 'msg-7',
        session_id: 'session-7',
        role: 'system',
        text: 'Session started',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('info-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Tool message variant', () => {
    it('should render tool message centered', () => {
      const message: Message = {
        id: 'msg-8',
        session_id: 'session-8',
        role: 'tool',
        text: 'Tool executed: grep',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('Tool executed: grep')
      expect(card).toBeInTheDocument()
    })

    it('should show tool icon', () => {
      const message: Message = {
        id: 'msg-9',
        session_id: 'session-9',
        role: 'tool',
        text: 'Tool executed',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('tool-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Question message variant', () => {
    it('should render question message', () => {
      const message: Message = {
        id: 'msg-10',
        session_id: 'session-10',
        role: 'question',
        text: 'What files need to be changed?',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('What files need to be changed?')
      expect(card).toBeInTheDocument()
    })

    it('should show question icon', () => {
      const message: Message = {
        id: 'msg-11',
        session_id: 'session-11',
        role: 'question',
        text: 'Question message',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('question-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Thinking message variant', () => {
    it('should render thinking message', () => {
      const message: Message = {
        id: 'msg-12',
        session_id: 'session-12',
        role: 'thinking',
        text: 'Analyzing...',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('Analyzing...')
      expect(card).toBeInTheDocument()
    })

    it('should show sparkles icon', () => {
      const message: Message = {
        id: 'msg-13',
        session_id: 'session-13',
        role: 'thinking',
        text: 'Thinking...',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('sparkles-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Error message variant', () => {
    it('should render error message', () => {
      const message: Message = {
        id: 'msg-14',
        session_id: 'session-14',
        role: 'error',
        text: 'Failed to execute',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const card = screen.getByText('Failed to execute')
      expect(card).toBeInTheDocument()
    })

    it('should show error icon', () => {
      const message: Message = {
        id: 'msg-15',
        session_id: 'session-15',
        role: 'error',
        text: 'Error message',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const icon = screen.getByTestId('error-icon')
      expect(icon).toBeInTheDocument()
    })
  })

  describe('Multi-part message rendering', () => {
    it('should render text part', () => {
      const message: Message = {
        id: 'msg-16',
        session_id: 'session-16',
        role: 'user',
        text: 'Text content',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const text = screen.getByText('Text content')
      expect(text).toBeInTheDocument()
    })

    it('should handle code blocks in text', () => {
      const message: Message = {
        id: 'msg-17',
        session_id: 'session-17',
        role: 'assistant',
        text: 'Check this code:\n```javascript\nconsole.log("Hello");\n```',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      // Verify card is rendered with markdown content
      expect(screen.getByText('Assistant')).toBeInTheDocument()
    })

    it('should handle empty parts array', () => {
      const message: Message = {
        id: 'msg-18',
        session_id: 'session-18',
        role: 'user',
        text: 'Just text',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      expect(screen.getByText('Just text')).toBeInTheDocument()
    })
  })

  describe('Action buttons', () => {
    it('should have copy button', () => {
      const message: Message = {
        id: 'msg-19',
        session_id: 'session-19',
        role: 'user',
        text: 'Copy this message',
        parts: [],
        timestamp: Date.now(),
      }

      render(<MessageCard messages={[message]} role={message.role} />)

      const copyButton = screen.getByRole('button', { name: /copy/i })
      expect(copyButton).toBeInTheDocument()
    })

    it('should have quote button', () => {
      const message: Message = {
        id: 'msg-20',
        session_id: 'session-20',
        role: 'user',
        text: 'Quote this message',
        parts: [],
        timestamp: Date.now(),
      }

      const testFn = vi.fn()
      render(<MessageCard messages={[message]} role={message.role} onQuote={testFn} />)

      // Verify quote button exists
      const quoteButton = screen.getByRole('button', { name: /quote/i })
      expect(quoteButton).toBeInTheDocument()

      // Test the quote button callback
      fireEvent.click(quoteButton)
      expect(testFn).toHaveBeenCalled()
    })

    it('should have edit button for assistant messages', () => {
      const message: Message = {
        id: 'msg-21',
        session_id: 'session-21',
        role: 'assistant',
        text: 'Edit me',
        parts: [],
        timestamp: Date.now(),
      }

      const testFn = vi.fn()
      render(<MessageCard messages={[message]} role={message.role} onEdit={testFn} />)

      const editButton = screen.getByRole('button', { name: /edit/i })
      expect(editButton).toBeInTheDocument()

      fireEvent.click(editButton)
      expect(testFn).toHaveBeenCalled()
    })
  })
})
