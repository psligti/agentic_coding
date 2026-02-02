import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

describe('App', () => {
  it('renders Vite + React heading', () => {
    render(<App />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Vite + React')
  })

  it('renders the count button', () => {
    render(<App />)
    expect(screen.getByRole('button')).toBeInTheDocument()
  })

  it('renders edit instruction', () => {
    render(<App />)
    expect(screen.getByText(/Edit/)).toBeInTheDocument()
  })
})
