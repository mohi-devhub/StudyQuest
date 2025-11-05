'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'

interface TopicData {
  topic: string
  avg_score: number
  total_attempts: number
  last_attempt: string
}

interface TopicCardProps {
  topic: TopicData
  delay?: number
}

export default function TopicCard({ topic, delay = 0 }: TopicCardProps) {
  const router = useRouter()
  
  const daysSinceAttempt = Math.floor(
    (Date.now() - new Date(topic.last_attempt).getTime()) / (1000 * 60 * 60 * 24)
  )

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-terminal-white'
    if (score >= 70) return 'text-terminal-gray'
    return 'text-terminal-gray opacity-70'
  }

  const handleCardClick = () => {
    // Determine difficulty based on current score
    let difficulty = 'medium'
    if (topic.avg_score >= 85) difficulty = 'hard'
    else if (topic.avg_score >= 95) difficulty = 'expert'
    else if (topic.avg_score < 70) difficulty = 'easy'
    
    router.push(`/quiz?topic=${encodeURIComponent(topic.topic)}&difficulty=${difficulty}`)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      onClick={handleCardClick}
      whileHover={{ scale: 1.02, transition: { duration: 0.1 } }}
      className="border border-terminal-white p-5 bg-terminal-black cursor-pointer group"
      style={{ backgroundColor: '#000000' }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-medium group-hover:underline">
            {topic.topic}
          </h3>
          <div className="text-terminal-gray text-xs mt-1">
            {daysSinceAttempt === 0 ? 'Today' : `${daysSinceAttempt}d ago`} · {topic.total_attempts} attempts
          </div>
        </div>
      </div>

      {/* Score Display */}
      <div className="flex items-end justify-between">
        <div>
          <div className="text-terminal-gray text-xs mb-1">AVG_SCORE</div>
          <div className={`text-3xl font-bold ${getScoreColor(topic.avg_score)}`}>
            {topic.avg_score.toFixed(1)}%
          </div>
        </div>

        {/* Visual score indicator */}
        <div className="flex items-end space-x-1 h-12">
          {[...Array(5)].map((_, i) => {
            const threshold = (i + 1) * 20
            const isActive = topic.avg_score >= threshold
            return (
              <motion.div
                key={i}
                initial={{ height: 0 }}
                animate={{ height: `${(i + 1) * 20}%` }}
                transition={{ delay: delay + 0.1 + i * 0.05 }}
                className={`w-2 border ${
                  isActive 
                    ? 'border-terminal-white bg-terminal-white' 
                    : 'border-terminal-gray'
                }`}
              />
            )
          })}
        </div>
      </div>
    </motion.div>
  )
}
