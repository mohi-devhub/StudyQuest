import { render, screen, waitFor } from '@testing-library/react'
import CoachFeedbackPanel from '../CoachFeedbackPanel'

// Mock fetch
global.fetch = jest.fn()

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}))

describe('CoachFeedbackPanel', () => {
  const mockFeedback = {
    success: true,
    user_id: 'test_user_123',
    performance_summary: {
      average_score: 75.5,
      total_quizzes: 10,
      level: 3,
      total_xp: 1250,
      weak_topics_count: 2,
      strong_topics_count: 3,
    },
    weak_topics: [
      {
        topic: 'Python Basics',
        score: 55.0,
        attempts: 3,
        recommendation: 'Review fundamental concepts and practice more',
      },
      {
        topic: 'Data Structures',
        score: 58.5,
        attempts: 2,
        recommendation: 'Focus on arrays and linked lists',
      },
    ],
    recommended_topics: [
      'JavaScript Fundamentals',
      'Web Development',
      'Database Design',
    ],
    motivational_messages: [
      'Great progress! Keep up the good work!',
      'You are improving steadily.',
    ],
    next_steps: [
      'Review weak topics',
      'Try harder difficulty levels',
      'Complete daily challenges',
    ],
  }

  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders loading state initially', () => {
    ;(global.fetch as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )

    render(<CoachFeedbackPanel userId="test_user" />)

    expect(screen.getByText(/LOADING COACH FEEDBACK/i)).toBeInTheDocument()
  })

  it('renders feedback data correctly', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFeedback,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText('ADAPTIVE COACH FEEDBACK')).toBeInTheDocument()
    })

    // Check motivational messages
    expect(screen.getByText('Great progress! Keep up the good work!')).toBeInTheDocument()
    expect(screen.getByText('You are improving steadily.')).toBeInTheDocument()

    // Check weak topics
    expect(screen.getByText(/Python Basics/)).toBeInTheDocument()
    expect(screen.getByText(/Data Structures/)).toBeInTheDocument()
    expect(screen.getByText('55%')).toBeInTheDocument()
    expect(screen.getByText('58%')).toBeInTheDocument()

    // Check recommended topics
    expect(screen.getByText('JavaScript Fundamentals')).toBeInTheDocument()
    expect(screen.getByText('Web Development')).toBeInTheDocument()
    expect(screen.getByText('Database Design')).toBeInTheDocument()

    // Check next steps
    expect(screen.getByText('Review weak topics')).toBeInTheDocument()
    expect(screen.getByText('Try harder difficulty levels')).toBeInTheDocument()
    expect(screen.getByText('Complete daily challenges')).toBeInTheDocument()
  })

  it('renders error state when fetch fails', async () => {
    ;(global.fetch as jest.Mock).mockRejectedValueOnce(
      new Error('Failed to fetch')
    )

    render(<CoachFeedbackPanel userId="test_user" />)

    await waitFor(() => {
      expect(
        screen.getByText(/Coach feedback temporarily unavailable/i)
      ).toBeInTheDocument()
    })
  })

  it('renders error state when response is not ok', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
    })

    render(<CoachFeedbackPanel userId="test_user" />)

    await waitFor(() => {
      expect(
        screen.getByText(/Coach feedback temporarily unavailable/i)
      ).toBeInTheDocument()
    })
  })

  it('displays performance summary correctly', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFeedback,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText(/avg_score: 75.5%/)).toBeInTheDocument()
      expect(screen.getByText(/quizzes: 10/)).toBeInTheDocument()
      expect(screen.getByText(/weak: 2/)).toBeInTheDocument()
      expect(screen.getByText(/strong: 3/)).toBeInTheDocument()
    })
  })

  it('renders weak topics with recommendations', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFeedback,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(
        screen.getByText('Review fundamental concepts and practice more')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Focus on arrays and linked lists')
      ).toBeInTheDocument()
    })
  })

  it('displays attempt counts for weak topics', async () => {
    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockFeedback,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText('3 attempts')).toBeInTheDocument()
      expect(screen.getByText('2 attempts')).toBeInTheDocument()
    })
  })

  it('handles empty weak topics array', async () => {
    const feedbackWithoutWeakTopics = {
      ...mockFeedback,
      weak_topics: [],
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => feedbackWithoutWeakTopics,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText('ADAPTIVE COACH FEEDBACK')).toBeInTheDocument()
    })

    // Should not show weak topics section
    expect(screen.queryByText(/TOPICS_TO_REVIEW/)).not.toBeInTheDocument()
  })

  it('handles empty recommended topics array', async () => {
    const feedbackWithoutRecommendations = {
      ...mockFeedback,
      recommended_topics: [],
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => feedbackWithoutRecommendations,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText('ADAPTIVE COACH FEEDBACK')).toBeInTheDocument()
    })

    // Should not show recommended topics section
    expect(screen.queryByText(/RECOMMENDED_NEXT_TOPICS/)).not.toBeInTheDocument()
  })

  it('handles empty motivational messages array', async () => {
    const feedbackWithoutMessages = {
      ...mockFeedback,
      motivational_messages: [],
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => feedbackWithoutMessages,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText('ADAPTIVE COACH FEEDBACK')).toBeInTheDocument()
    })

    // Should not show motivational messages
    expect(
      screen.queryByText('Great progress! Keep up the good work!')
    ).not.toBeInTheDocument()
  })

  it('handles empty next steps array', async () => {
    const feedbackWithoutNextSteps = {
      ...mockFeedback,
      next_steps: [],
    }

    ;(global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => feedbackWithoutNextSteps,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(screen.getByText('ADAPTIVE COACH FEEDBACK')).toBeInTheDocument()
    })

    // Should not show next steps section
    expect(screen.queryByText(/NEXT_STEPS/)).not.toBeInTheDocument()
  })

  it('uses correct API endpoint', async () => {
    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFeedback,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/coach/feedback/test_user_123')
      )
    })
  })

  it('respects NEXT_PUBLIC_API_URL environment variable', async () => {
    const originalEnv = process.env.NEXT_PUBLIC_API_URL
    process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com'

    const mockFetch = global.fetch as jest.Mock
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockFeedback,
    })

    render(<CoachFeedbackPanel userId="test_user_123" />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/coach/feedback/test_user_123'
      )
    })

    // Restore original env
    process.env.NEXT_PUBLIC_API_URL = originalEnv
  })
})
