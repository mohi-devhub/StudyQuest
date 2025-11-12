import { render, screen, fireEvent } from '@testing-library/react'
import { useRouter } from 'next/navigation'
import TopicCard from '../TopicCard'

// Mock the router
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}))

describe('TopicCard', () => {
  const mockPush = jest.fn()
  const mockTopic = {
    topic: 'JavaScript Basics',
    avg_score: 85.5,
    total_attempts: 3,
    last_attempt: new Date('2025-01-01').toISOString(),
  }

  beforeEach(() => {
    jest.clearAllMocks()
    ;(useRouter as jest.Mock).mockReturnValue({
      push: mockPush,
    })
  })

  it('renders topic information correctly', () => {
    render(<TopicCard topic={mockTopic} />)

    expect(screen.getByText('JavaScript Basics')).toBeInTheDocument()
    expect(screen.getByText('85.5%')).toBeInTheDocument()
    expect(screen.getByText(/3 attempts/)).toBeInTheDocument()
  })

  it('navigates to quiz page when clicked', () => {
    render(<TopicCard topic={mockTopic} />)

    const card = screen.getByText('JavaScript Basics').closest('div')
    fireEvent.click(card!)

    expect(mockPush).toHaveBeenCalledWith(
      expect.stringContaining('/quiz?topic=JavaScript%20Basics')
    )
  })

  it('applies correct difficulty based on score', () => {
    const highScoreTopic = { ...mockTopic, avg_score: 96 }
    render(<TopicCard topic={highScoreTopic} />)

    const card = screen.getByText('JavaScript Basics').closest('div')
    fireEvent.click(card!)

    expect(mockPush).toHaveBeenCalledWith(
      expect.stringContaining('difficulty=expert')
    )
  })

  it('shows correct score color for high score', () => {
    render(<TopicCard topic={mockTopic} />)

    const scoreElement = screen.getByText('85.5%')
    expect(scoreElement).toHaveClass('text-terminal-white')
  })

  it('shows correct score color for low score', () => {
    const lowScoreTopic = { ...mockTopic, avg_score: 65 }
    render(<TopicCard topic={lowScoreTopic} />)

    const scoreElement = screen.getByText('65.0%')
    expect(scoreElement).toHaveClass('opacity-70')
  })

  it('displays score bars correctly', () => {
    render(<TopicCard topic={mockTopic} />)

    // Should have 5 score bars
    const bars = screen.getAllByRole('generic').filter(
      (el) => el.className.includes('w-2')
    )
    expect(bars.length).toBe(5)
  })

  it('formats relative time correctly', () => {
    render(<TopicCard topic={mockTopic} />)

    // Should show some time indication
    expect(screen.getByText(/ago|Today/)).toBeInTheDocument()
  })
})
