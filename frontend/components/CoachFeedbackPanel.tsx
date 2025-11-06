'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

interface CoachFeedback {
  success: boolean
  user_id: string
  performance_summary: {
    average_score: number
    total_quizzes: number
    level: number
    total_xp: number
    weak_topics_count: number
    strong_topics_count: number
  }
  weak_topics: Array<{
    topic: string
    score: number
    attempts: number
    recommendation: string
  }>
  recommended_topics: string[]
  motivational_messages: string[]
  next_steps: string[]
}

interface CoachFeedbackProps {
  userId: string
}

export default function CoachFeedbackPanel({ userId }: CoachFeedbackProps) {
  const [feedback, setFeedback] = useState<CoachFeedback | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchFeedback()
  }, [userId])

  const fetchFeedback = async () => {
    try {
      setLoading(true)
      setError(null)

      const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE}/coach/feedback/${userId}`)
      
      if (!response.ok) {
        throw new Error('Failed to fetch coach feedback')
      }

      const data = await response.json()
      setFeedback(data)
    } catch (err: any) {
      setError(err.message)
      console.error('Coach feedback error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="border border-gray-700 p-6 bg-black">
        <div className="text-gray-500 text-center">
          <div className="animate-pulse">// LOADING COACH FEEDBACK...</div>
        </div>
      </div>
    )
  }

  if (error || !feedback) {
    return (
      <div className="border border-gray-700 p-6 bg-black">
        <div className="text-gray-600 text-center text-sm">
          // Coach feedback temporarily unavailable
        </div>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border border-white bg-black"
    >
      {/* Header */}
      <div className="bg-white text-black px-6 py-3 border-b border-white">
        <h2 className="text-xl font-bold">ADAPTIVE COACH FEEDBACK</h2>
      </div>

      <div className="p-6 space-y-6">
        {/* Motivational Messages */}
        {feedback.motivational_messages.length > 0 && (
          <div className="border border-gray-700 p-4 bg-black">
            <div className="space-y-2">
              {feedback.motivational_messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="text-white font-mono text-lg"
                >
                  {message}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Weak Topics - Need Review */}
        {feedback.weak_topics.length > 0 && (
          <div>
            <div className="text-sm text-gray-500 mb-3">
              // TOPICS_TO_REVIEW (SCORE &lt; 60%)
            </div>
            <div className="border border-gray-700 divide-y divide-gray-800">
              {feedback.weak_topics.map((topic, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.05 }}
                  className="p-4 hover:bg-gray-900 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-white font-bold mb-1">
                        [!] {topic.topic}
                      </div>
                      <div className="text-gray-500 text-sm">
                        {topic.recommendation}
                      </div>
                    </div>
                    <div className="text-right ml-4">
                      <div className="text-red-500 font-bold font-mono">
                        {topic.score.toFixed(0)}%
                      </div>
                      <div className="text-gray-600 text-xs">
                        {topic.attempts} attempts
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Topics */}
        {feedback.recommended_topics.length > 0 && (
          <div>
            <div className="text-sm text-gray-500 mb-3">
              // RECOMMENDED_NEXT_TOPICS
            </div>
            <div className="border border-gray-700 p-4 bg-black">
              <div className="space-y-2">
                {feedback.recommended_topics.map((topic, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 + index * 0.05 }}
                    className="text-white font-mono flex items-center"
                  >
                    <span className="text-gray-600 mr-3">
                      {(index + 1).toString().padStart(2, '0')}.
                    </span>
                    <span className="hover:text-gray-300 cursor-pointer transition-colors">
                      {topic}
                    </span>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Next Steps */}
        {feedback.next_steps.length > 0 && (
          <div>
            <div className="text-sm text-gray-500 mb-3">
              // NEXT_STEPS
            </div>
            <div className="border border-gray-700 p-4 bg-black">
              <div className="space-y-2">
                {feedback.next_steps.map((step, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + index * 0.05 }}
                    className="text-white font-mono flex items-start"
                  >
                    <span className="text-green-500 mr-3">▸</span>
                    <span>{step}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Performance Summary */}
        <div className="border-t border-gray-800 pt-4 mt-4">
          <div className="text-xs text-gray-600 space-y-1 font-mono">
            <div>
              $ coach.analyze(user_id=&quot;{feedback.user_id}&quot;)
            </div>
            <div>
              → avg_score: {feedback.performance_summary.average_score}% | 
              quizzes: {feedback.performance_summary.total_quizzes} | 
              weak: {feedback.performance_summary.weak_topics_count} | 
              strong: {feedback.performance_summary.strong_topics_count}
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
