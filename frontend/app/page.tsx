'use client'

import { useEffect, useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import Header from '@/components/Header'
import XPProgressBar from '@/components/XPProgressBar'
import TopicCard from '@/components/TopicCard'
import RecommendedCard from '@/components/RecommendedCard'
import LoadingScreen from '@/components/LoadingScreen'
import { useToast } from '@/components/Toast'
import { useRealtimeXP } from '@/lib/useRealtimeXP'

interface UserProgress {
  user_id: string
  total_xp: number
  level: number
  topics: Array<{
    topic: string
    avg_score: number
    total_attempts: number
    last_attempt: string
  }>
}

interface Recommendation {
  topic: string
  reason: string
  priority: string
  category: string
  current_score: number | null
  recommended_difficulty: string
  estimated_xp_gain: number
  urgency: string
}

interface RecommendationResponse {
  recommendations: Recommendation[]
  overall_stats?: {
    total_attempts: number
    avg_score: number
    topics_studied: number
  }
  ai_insights?: {
    motivational_message: string
    learning_insight: string
    priority_advice: string
  }
}

export default function Dashboard() {
  const [progress, setProgress] = useState<UserProgress | null>(null)
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Real-time updates
  const { showToast, ToastContainer } = useToast()
  
  // Stable callbacks for real-time events
  const handleXPGain = useCallback((xp: number, source: string, topic: string) => {
    console.log(`XP Gained: +${xp} from ${source} on ${topic}`)
    showToast(`${topic} completed!`, xp, 'xp')
    
    // Update progress with new XP
    setProgress(prev => {
      if (!prev) return prev
      return {
        ...prev,
        total_xp: prev.total_xp + xp,
        level: Math.floor((prev.total_xp + xp) / 500) + 1
      }
    })
  }, [showToast])

  const handleLevelUp = useCallback((newLevel: number) => {
    console.log(`Level Up! New level: ${newLevel}`)
    showToast(`LEVEL UP! Now level ${newLevel}`, undefined, 'success')
  }, [showToast])

  const handleProgressUpdate = useCallback((topic: string, newAvgScore: number) => {
    console.log(`Progress updated: ${topic} - ${newAvgScore}%`)
    
    // Update topic in progress
    setProgress(prev => {
      if (!prev) return prev
      return {
        ...prev,
        topics: prev.topics.map(t => 
          t.topic === topic ? { ...t, avg_score: newAvgScore } : t
        )
      }
    })
  }, [])
  
  // Subscribe to real-time XP updates
  const { isConnected } = useRealtimeXP({
    userId: 'demo_user',
    onXPGain: handleXPGain,
    onLevelUp: handleLevelUp,
    onProgressUpdate: handleProgressUpdate
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Mock token - replace with actual auth
      const token = 'your_token_here' // TODO: Implement actual auth
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

      // For demo purposes, we'll use mock data
      // In production, uncomment the API calls below

      // Fetch progress
      // const progressRes = await fetch(`${apiUrl}/progress/user123`, {
      //   headers: { 'Authorization': `Bearer ${token}` }
      // })
      // const progressData = await progressRes.json()
      
      // Fetch recommendations
      // const recRes = await fetch(`${apiUrl}/study/recommendations`, {
      //   headers: { 'Authorization': `Bearer ${token}` }
      // })
      // const recData = await recRes.json()

      // Mock data for demonstration
      const mockProgress: UserProgress = {
        user_id: 'demo_user',
        total_xp: 2450,
        level: 5,
        topics: [
          {
            topic: 'Python Programming',
            avg_score: 88.5,
            total_attempts: 12,
            last_attempt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            topic: 'Data Structures',
            avg_score: 68.0,
            total_attempts: 7,
            last_attempt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            topic: 'Algorithms',
            avg_score: 45.0,
            total_attempts: 5,
            last_attempt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString()
          },
          {
            topic: 'Web Development',
            avg_score: 72.0,
            total_attempts: 8,
            last_attempt: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString()
          }
        ]
      }

      const mockRecommendations: RecommendationResponse = {
        recommendations: [
          {
            topic: 'Algorithms',
            reason: 'Improve performance (current: 45%, goal: 70%+)',
            priority: 'high',
            category: 'weak_area',
            current_score: 45.0,
            recommended_difficulty: 'easy',
            estimated_xp_gain: 132,
            urgency: 'Address gaps in understanding'
          },
          {
            topic: 'Data Structures',
            reason: 'Improve performance (current: 68%, goal: 70%+)',
            priority: 'high',
            category: 'weak_area',
            current_score: 68.0,
            recommended_difficulty: 'medium',
            estimated_xp_gain: 151,
            urgency: 'Address gaps in understanding'
          },
          {
            topic: 'Web Development',
            reason: 'Review needed (last attempt: 15 days ago)',
            priority: 'medium',
            category: 'review',
            current_score: 72.0,
            recommended_difficulty: 'medium',
            estimated_xp_gain: 150,
            urgency: 'Maintain knowledge retention'
          }
        ],
        overall_stats: {
          total_attempts: 32,
          avg_score: 68.4,
          topics_studied: 4
        },
        ai_insights: {
          motivational_message: 'Great progress! Focus on Algorithms to strengthen your foundation.',
          learning_insight: 'Your Python skills are excellent. Build on that momentum with related topics.',
          priority_advice: 'Start with easy-level Algorithms quizzes to build confidence and understanding.'
        }
      }

      setProgress(mockProgress)
      setRecommendations(mockRecommendations)
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error('Dashboard error:', err)
    } finally {
      setTimeout(() => setLoading(false), 800) // Smooth transition
    }
  }

  if (loading) {
    return <LoadingScreen />
  }

  if (error) {
    return (
      <div className="min-h-screen bg-terminal-black flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border border-terminal-white p-8 max-w-md w-full"
        >
          <h2 className="text-2xl mb-4">// ERROR</h2>
          <p className="text-terminal-gray mb-6">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="w-full bg-terminal-black text-terminal-white border border-terminal-white px-6 py-3 hover:bg-terminal-white hover:text-terminal-black transition-colors"
          >
            RETRY
          </button>
        </motion.div>
      </div>
    )
  }

  if (!progress || !recommendations) {
    return null
  }

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <Header />

        {/* XP Progress Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mt-8"
        >
          <XPProgressBar 
            currentXP={progress.total_xp} 
            level={progress.level}
          />
        </motion.div>

        {/* Stats Overview */}
        {recommendations.overall_stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div className="border border-terminal-white p-4">
              <div className="text-terminal-gray text-sm mb-1">// TOTAL_QUIZZES</div>
              <div className="text-3xl font-bold">{recommendations.overall_stats.total_attempts}</div>
            </div>
            <div className="border border-terminal-white p-4">
              <div className="text-terminal-gray text-sm mb-1">// AVG_SCORE</div>
              <div className="text-3xl font-bold">{recommendations.overall_stats.avg_score.toFixed(1)}%</div>
            </div>
            <div className="border border-terminal-white p-4">
              <div className="text-terminal-gray text-sm mb-1">// TOPICS_STUDIED</div>
              <div className="text-3xl font-bold">{recommendations.overall_stats.topics_studied}</div>
            </div>
          </motion.div>
        )}

        {/* AI Insights */}
        {recommendations.ai_insights && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-8 border border-terminal-gray p-6"
          >
            <div className="text-sm text-terminal-gray mb-2">// AI_INSIGHTS</div>
            <p className="text-terminal-white mb-4">{recommendations.ai_insights.motivational_message}</p>
            <p className="text-terminal-gray text-sm">{recommendations.ai_insights.priority_advice}</p>
          </motion.div>
        )}

        {/* Recommended Topic (Top Priority) */}
        {recommendations.recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-8"
          >
            <h2 className="text-xl mb-4">// NEXT_RECOMMENDED</h2>
            <RecommendedCard recommendation={recommendations.recommendations[0]} />
          </motion.div>
        )}

        {/* Recent Topics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12"
        >
          <h2 className="text-xl mb-4">// YOUR_TOPICS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {progress.topics.map((topic, index) => (
              <TopicCard 
                key={topic.topic} 
                topic={topic} 
                delay={0.6 + index * 0.1}
              />
            ))}
          </div>
        </motion.div>

        {/* Other Recommendations */}
        {recommendations.recommendations.length > 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-12"
          >
            <h2 className="text-xl mb-4">// OTHER_RECOMMENDATIONS</h2>
            <div className="space-y-3">
              {recommendations.recommendations.slice(1, 4).map((rec, index) => (
                <motion.div
                  key={rec.topic}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.9 + index * 0.1 }}
                  className="border border-terminal-gray p-4 hover:border-terminal-white transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="text-sm text-terminal-gray mb-1">
                        [{rec.priority.toUpperCase()}] {rec.category}
                      </div>
                      <div className="text-lg font-medium">{rec.topic}</div>
                    </div>
                    <div className="text-terminal-gray text-sm">
                      +{rec.estimated_xp_gain} XP
                    </div>
                  </div>
                  <div className="text-sm text-terminal-gray">{rec.reason}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-16 pt-8 border-t border-terminal-gray text-center text-terminal-gray text-sm"
        >
          <p>StudyQuest v1.0 // Monochrome Terminal Dashboard</p>
          <p className="mt-2">
            Real-time updates: {isConnected ? '🟢 CONNECTED' : '🔴 DISCONNECTED'}
          </p>
        </motion.div>
      </div>
      
      {/* Toast Notifications */}
      <ToastContainer />
    </div>
  )
}
