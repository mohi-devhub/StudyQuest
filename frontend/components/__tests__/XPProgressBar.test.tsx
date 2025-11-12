import { render, screen } from '@testing-library/react'
import XPProgressBar from '../XPProgressBar'

describe('XPProgressBar', () => {
  it('renders the progress bar with correct values', () => {
    render(<XPProgressBar currentXP={1250} level={3} />)

    // Check for level display
    expect(screen.getByText(/LEVEL 3/)).toBeInTheDocument()

    // Check for XP display
    expect(screen.getByText(/250 \/ 500 XP to Level 4/)).toBeInTheDocument()

    // Check for progress bar
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '50')
  })

  it('handles zero XP correctly', () => {
    render(<XPProgressBar currentXP={1000} level={3} />)

    // Check for level display
    expect(screen.getByText(/LEVEL 3/)).toBeInTheDocument()

    // Check for XP display
    expect(screen.getByText(/0 \/ 500 XP to Level 4/)).toBeInTheDocument()

    // Check for progress bar
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '0')
  })

  it('handles full XP bar correctly', () => {
    render(<XPProgressBar currentXP={1499} level={3} />)

    // Check for level display
    expect(screen.getByText(/LEVEL 3/)).toBeInTheDocument()

    // Check for XP display
    expect(screen.getByText(/499 \/ 500 XP to Level 4/)).toBeInTheDocument()

    // Check for progress bar
    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '99.8')
  })
})
