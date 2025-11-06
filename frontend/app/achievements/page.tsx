'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'

interface Badge {
  id: string
  badge_key: string
  name: string
  description: string
  symbol: string
  tier: number
  category: string
  unlocked_at: string
  seen: boolean
  metadata: any
}

interface Achievement {
  total_badges: number
  bronze_badges: number
  silver_badges: number
  gold_badges: number
  platinum_badges: number
  total_milestones: number
  latest_badge_at: string | null
}

export default function AchievementsPage() {
  const [badges, setBadges] = useState<Badge[]>([])
  const [summary, setSummary] = useState<Achievement | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const userId = 'demo_user' // In production, get from auth

  useEffect(() => {
    fetchAchievements()
  }, [])

  const fetchAchievements = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch user badges
      const badgesRes = await fetch(`/api/achievements/user/${userId}/badges`)
      if (!badgesRes.ok) throw new Error('Failed to fetch badges')
      const badgesData = await badgesRes.json()

      // Fetch summary
      const summaryRes = await fetch(`/api/achievements/user/${userId}/summary`)
      if (!summaryRes.ok) throw new Error('Failed to fetch summary')
      const summaryData = await summaryRes.json()

      setBadges(badgesData.badges || [])
      setSummary(summaryData)
    } catch (err: any) {
      setError(err.message)
      console.error('Achievements error:', err)
    } finally {
      setLoading(false)
    }
  }

  const getTierName = (tier: number): string => {
    switch (tier) {
      case 1: return 'BRONZE'
      case 2: return 'SILVER'
      case 3: return 'GOLD'
      case 4: return 'PLATINUM'
      default: return 'UNKNOWN'
    }
  }

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-GB', { 
      day: '2-digit', 
      month: 'short', 
      year: 'numeric' 
    }).toUpperCase()
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center font-mono"
        >
          <div className="text-white text-xl">
            LOADING ACHIEVEMENTS<span className="animate-pulse">...</span>
          </div>
          <div className="text-gray-500 text-sm mt-2">
            // Fetching badges and milestones
          </div>
        </motion.div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border border-white p-8 max-w-md w-full font-mono"
        >
          <h2 className="text-2xl mb-4 text-white">// ERROR</h2>
          <p className="text-gray-500 mb-6">{error}</p>
          <button
            onClick={fetchAchievements}
            className="w-full bg-black text-white border border-white px-6 py-3 hover:bg-white hover:text-black transition-colors"
          >
            RETRY
          </button>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-8 font-mono">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link
            href="/"
            className="text-gray-500 text-sm hover:text-white transition-colors mb-4 inline-block"
          >
            ← BACK_TO_DASHBOARD
          </Link>
          <div className="bg-white text-black px-6 py-4">
            <h1 className="text-3xl font-bold text-center">
              ════════ ACHIEVEMENTS ════════
            </h1>
          </div>
        </motion.div>

        {/* Summary Stats */}
        {summary && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="border border-gray-500 p-6 mb-8"
          >
            <h2 className="text-xl mb-4 text-white border-b border-gray-500 pb-2">
              // BADGE_SUMMARY
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{summary.total_badges}</div>
                <div className="text-sm text-gray-500 mt-1">TOTAL</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{summary.bronze_badges}</div>
                <div className="text-sm text-gray-500 mt-1">BRONZE</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{summary.silver_badges}</div>
                <div className="text-sm text-gray-500 mt-1">SILVER</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{summary.gold_badges}</div>
                <div className="text-sm text-gray-500 mt-1">GOLD</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-white">{summary.platinum_badges}</div>
                <div className="text-sm text-gray-500 mt-1">PLATINUM</div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Badges List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="border border-gray-500 mb-8"
        >
          <div className="bg-white text-black px-6 py-3">
            <h2 className="text-xl font-bold">UNLOCKED BADGES ({badges.length})</h2>
          </div>

          {badges.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <div className="text-lg mb-2">NO BADGES YET</div>
              <div className="text-sm">// Complete quizzes and level up to earn badges</div>
            </div>
          ) : (
            <div className="divide-y divide-gray-800">
              {badges.map((badge, index) => (
                <motion.div
                  key={badge.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.05 }}
                  className="p-6 hover:bg-gray-900 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      {/* Symbol and Name */}
                      <div className="flex items-center gap-4 mb-2">
                        <span className="text-3xl text-white">{badge.symbol}</span>
                        <div>
                          <h3 className="text-xl font-bold text-white">{badge.name}</h3>
                          <div className="flex items-center gap-3 mt-1">
                            <span className="text-xs text-gray-500 uppercase border border-gray-700 px-2 py-1">
                              {getTierName(badge.tier)}
                            </span>
                            <span className="text-xs text-gray-500 uppercase">
                              {badge.category}
                            </span>
                          </div>
                        </div>
                      </div>

                      {/* Description */}
                      <p className="text-gray-400 text-sm ml-14 mb-2">
                        {badge.description}
                      </p>

                      {/* Unlock Date */}
                      <div className="text-xs text-gray-600 ml-14">
                        Unlocked on {formatDate(badge.unlocked_at)}
                      </div>
                    </div>

                    {/* New indicator */}
                    {!badge.seen && (
                      <div className="text-xs text-white border border-white px-2 py-1">
                        NEW
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Badge Tier Legend */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="border border-gray-800 p-6"
        >
          <h3 className="text-sm text-gray-500 mb-4">// TIER_SYSTEM</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <div className="text-white font-bold mb-1">[★] BRONZE</div>
              <div className="text-gray-600">Entry-level achievements</div>
            </div>
            <div>
              <div className="text-white font-bold mb-1">[★★] SILVER</div>
              <div className="text-gray-600">Intermediate milestones</div>
            </div>
            <div>
              <div className="text-white font-bold mb-1">[★★★] GOLD</div>
              <div className="text-gray-600">Advanced accomplishments</div>
            </div>
            <div>
              <div className="text-white font-bold mb-1">[◆] PLATINUM</div>
              <div className="text-gray-600">Elite achievements</div>
            </div>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 text-center text-gray-600 text-xs space-y-2"
        >
          <p>Keep learning to unlock more badges!</p>
          <p className="font-mono">
            $ achievements --user=demo_user --format=terminal
          </p>
        </motion.div>
      </div>
    </div>
  )
}
