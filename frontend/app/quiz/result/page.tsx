'use client'

import { useEffect, useState } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import TypingText from '@/components/TypingText'

interface QuizResult {
  quiz_id: string
  user_id: string
  topic: string
  difficulty: string
  score: number
  total_questions: number
  correct_answers: number
  xp_gained: number
  performance_feedback: string
  next_difficulty: string
  timestamp: string
}

interface CoachFeedback {
  motivational_message: string
  learning_insight: string
  improvement_tip: string
  next_steps: string
}

export default function QuizResultPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [result, setResult] = useState<QuizResult | null>(null)
  const [coachFeedback, setCoachFeedback] = useState<CoachFeedback | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [playSound, setPlaySound] = useState(false)

  useEffect(() => {
    fetchQuizResult()
  }, [])

  const fetchQuizResult = async () => {
    try {
      setLoading(true)
      setError(null)

      // Get quiz ID from URL params
      const quizId = searchParams.get('id')
      
      if (!quizId) {
        // Use mock data for demonstration
        useMockData()
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const token = 'your_token_here' // TODO: Implement real auth

      // Fetch quiz result
      // const resultRes = await fetch(`${apiUrl}/quiz/result/${quizId}`, {
      //   headers: { 'Authorization': `Bearer ${token}` }
      // })
      // const resultData = await resultRes.json()

      // Fetch coach feedback
      // const feedbackRes = await fetch(`${apiUrl}/coach/feedback`, {
      //   method: 'POST',
      //   headers: {
      //     'Authorization': `Bearer ${token}`,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify({
      //     score: resultData.score,
      //     topic: resultData.topic,
      //     difficulty: resultData.difficulty
      //   })
      // })
      // const feedbackData = await feedbackRes.json()

      // For now, use mock data
      useMockData()
    } catch (err) {
      setError('Failed to load quiz results')
      console.error('Quiz result error:', err)
    } finally {
      setTimeout(() => setLoading(false), 1000)
    }
  }

  const useMockData = () => {
    const mockResult: QuizResult = {
      quiz_id: 'quiz_12345',
      user_id: 'demo_user',
      topic: 'Python Programming',
      difficulty: 'medium',
      score: 85,
      total_questions: 10,
      correct_answers: 8.5,
      xp_gained: 165,
      performance_feedback: 'Excellent performance! You demonstrated strong understanding of Python concepts.',
      next_difficulty: 'hard',
      timestamp: new Date().toISOString()
    }

    const mockFeedback: CoachFeedback = {
      motivational_message: "Outstanding work! You're showing great progress in Python Programming.",
      learning_insight: "Your strong performance on object-oriented questions shows solid fundamentals. Keep building on this foundation.",
      improvement_tip: "Consider reviewing list comprehensions and lambda functions - these areas showed slight hesitation.",
      next_steps: "Ready to challenge yourself? Try a hard-level quiz to push your boundaries and earn bonus XP!"
    }

    setResult(mockResult)
    setCoachFeedback(mockFeedback)
  }

  const handleRetryQuiz = () => {
    if (playSound) playClickSound()
    // Navigate to quiz page with same topic/difficulty
    router.push(`/quiz?topic=${encodeURIComponent(result?.topic || '')}&difficulty=${result?.difficulty}`)
  }

  const handleNextTopic = () => {
    if (playSound) playClickSound()
    // Navigate back to dashboard to see new recommendations
    router.push('/')
  }

  const playClickSound = () => {
    // Optional terminal click sound
    const audio = new Audio('/sounds/terminal-click.mp3')
    audio.volume = 0.3
    audio.play().catch(() => {
      // Silently fail if sound doesn't play
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-terminal-black flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="text-terminal-white text-xl font-mono mb-4">
            PROCESSING RESULTS<span className="animate-pulse">...</span>
          </div>
          <div className="text-terminal-gray text-sm">
            // Calculating XP and updating progress
          </div>
        </motion.div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="min-h-screen bg-terminal-black flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border border-terminal-white p-8 max-w-md w-full"
        >
          <h2 className="text-2xl mb-4">// ERROR</h2>
          <p className="text-terminal-gray mb-6">{error || 'Quiz results not found'}</p>
          <Link
            href="/"
            className="block w-full text-center bg-terminal-black text-terminal-white border border-terminal-white px-6 py-3 hover:bg-terminal-white hover:text-terminal-black transition-colors"
          >
            RETURN_TO_DASHBOARD()
          </Link>
        </motion.div>
      </div>
    )
  }

  const getPerformanceLevel = (score: number): string => {
    if (score >= 90) return 'EXCEPTIONAL'
    if (score >= 80) return 'EXCELLENT'
    if (score >= 70) return 'GOOD'
    if (score >= 60) return 'SATISFACTORY'
    return 'NEEDS_IMPROVEMENT'
  }

  const getDifficultyLabel = (difficulty: string): string => {
    const labels: { [key: string]: string } = {
      easy: '█░░░',
      medium: '██░░',
      hard: '███░',
      expert: '████'
    }
    return labels[difficulty.toLowerCase()] || '░░░░'
  }

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white p-6 md:p-8 font-mono">
      <div className="max-w-4xl mx-auto">
        {/* Header Banner */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-terminal-white text-terminal-black px-6 py-4 mb-8"
        >
          <h1 className="text-2xl font-bold tracking-tight text-center">
            ═══════════════ QUIZ SUMMARY ═══════════════
          </h1>
        </motion.div>

        {/* Terminal Output Container */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="border border-terminal-white p-8 space-y-6"
        >
          {/* Quiz Info Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
          >
            <div className="text-terminal-gray text-sm mb-2">// QUIZ_METADATA</div>
            <div className="pl-4 space-y-1">
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">├─ TOPIC:</span>
                <span className="text-terminal-white font-bold">{result.topic}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">├─ DIFFICULTY:</span>
                <span className="text-terminal-white">{getDifficultyLabel(result.difficulty)}</span>
                <span className="text-terminal-gray text-sm">({result.difficulty.toUpperCase()})</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">└─ TIMESTAMP:</span>
                <span className="text-terminal-gray text-sm">
                  {new Date(result.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          </motion.div>

          {/* Divider */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 0.4, duration: 0.5 }}
            className="border-t border-terminal-gray origin-left"
          />

          {/* Score Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <div className="text-terminal-gray text-sm mb-2">// PERFORMANCE_METRICS</div>
            <div className="pl-4 space-y-2">
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">├─ SCORE:</span>
                <span className="text-terminal-white text-3xl font-bold">{result.score}%</span>
                <span className={`text-sm ${result.score >= 70 ? 'text-terminal-white' : 'text-terminal-gray'}`}>
                  [{getPerformanceLevel(result.score)}]
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">├─ CORRECT:</span>
                <span className="text-terminal-white">{result.correct_answers} / {result.total_questions}</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">└─ ACCURACY:</span>
                <div className="flex-1">
                  <div className="h-4 border border-terminal-white max-w-xs relative overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${result.score}%` }}
                      transition={{ delay: 0.6, duration: 1, ease: 'easeOut' }}
                      className="h-full bg-terminal-white"
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>

          {/* Divider */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 0.7, duration: 0.5 }}
            className="border-t border-terminal-gray origin-left"
          />

          {/* XP Gained Section */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.8 }}
          >
            <div className="text-terminal-gray text-sm mb-2">// XP_REWARD</div>
            <div className="pl-4 space-y-2">
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">├─ XP_GAINED:</span>
                <motion.span
                  initial={{ scale: 1 }}
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ delay: 1, duration: 0.5 }}
                  className="text-terminal-white text-4xl font-bold"
                >
                  +{result.xp_gained}
                </motion.span>
                <span className="text-terminal-gray">XP</span>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-terminal-gray">├─ NEXT_DIFFICULTY:</span>
                <span className="text-terminal-white">{result.next_difficulty.toUpperCase()}</span>
              </div>
              <div className="flex items-start space-x-4">
                <span className="text-terminal-gray">└─ FEEDBACK:</span>
                <span className="text-terminal-gray flex-1 italic">
                  "{result.performance_feedback}"
                </span>
              </div>
            </div>
          </motion.div>

          {/* Divider */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 0.9, duration: 0.5 }}
            className="border-t border-terminal-gray origin-left"
          />

          {/* Coach Feedback Section */}
          {coachFeedback && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 1 }}
            >
              <div className="text-terminal-gray text-sm mb-2">// COACH_FEEDBACK</div>
              <div className="pl-4 space-y-3">
                <div className="space-y-1">
                  <div className="text-terminal-gray text-xs">├─ MOTIVATION:</div>
                  <div className="pl-4 text-terminal-white">
                    <TypingText 
                      text={coachFeedback.motivational_message}
                      speed={40}
                      delay={1100}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-terminal-gray text-xs">├─ INSIGHT:</div>
                  <div className="pl-4 text-terminal-gray">
                    <TypingText 
                      text={coachFeedback.learning_insight}
                      speed={40}
                      delay={1300}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-terminal-gray text-xs">├─ TIP:</div>
                  <div className="pl-4 text-terminal-gray">
                    <TypingText 
                      text={coachFeedback.improvement_tip}
                      speed={40}
                      delay={1500}
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <div className="text-terminal-gray text-xs">└─ NEXT_STEPS:</div>
                  <div className="pl-4 text-terminal-white">
                    <TypingText 
                      text={coachFeedback.next_steps}
                      speed={40}
                      delay={1700}
                    />
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {/* Divider */}
          <motion.div
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ delay: 1.1, duration: 0.5 }}
            className="border-t border-terminal-white origin-left"
          />

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            className="pt-4 grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleRetryQuiz}
              className="bg-terminal-black text-terminal-white border border-terminal-white px-8 py-4 hover:bg-terminal-white hover:text-terminal-black transition-all font-bold"
            >
              RETRY_QUIZ() →
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleNextTopic}
              className="bg-terminal-black text-terminal-white border border-terminal-white px-8 py-4 hover:bg-terminal-white hover:text-terminal-black transition-all font-bold"
            >
              NEXT_TOPIC() →
            </motion.button>
          </motion.div>

          {/* Return to Dashboard Link */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.3 }}
            className="pt-4 text-center"
          >
            <Link
              href="/"
              className="text-terminal-gray text-sm hover:text-terminal-white transition-colors underline"
            >
              ← RETURN_TO_DASHBOARD
            </Link>
          </motion.div>
        </motion.div>

        {/* Footer Terminal Prompt */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.4 }}
          className="mt-8 text-terminal-gray text-sm text-center"
        >
          <p>$ quiz_completed --status=success --xp=+{result.xp_gained}</p>
          <p className="mt-2">Progress automatically saved to database.</p>
        </motion.div>

        {/* Sound Toggle */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="mt-4 text-center"
        >
          <button
            onClick={() => setPlaySound(!playSound)}
            className="text-terminal-gray text-xs hover:text-terminal-white transition-colors"
          >
            [SOUND: {playSound ? 'ON' : 'OFF'}]
          </button>
        </motion.div>
      </div>
    </div>
  )
}
