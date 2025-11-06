'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface FeedbackFormData {
  category: string
  rating: number
  comments: string
  pageContext: string
}

export default function FeedbackPage() {
  const [formData, setFormData] = useState<FeedbackFormData>({
    category: 'general',
    rating: 5,
    comments: '',
    pageContext: 'feedback-page'
  })
  
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const categories = [
    { value: 'ux', label: 'User Experience', desc: 'Design, clarity, ease of use' },
    { value: 'speed', label: 'Performance', desc: 'Loading times, responsiveness' },
    { value: 'accuracy', label: 'Content Quality', desc: 'Quiz & study material accuracy' },
    { value: 'motivation', label: 'Engagement', desc: 'Motivation to learn' },
    { value: 'general', label: 'General Feedback', desc: 'Other suggestions' }
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Get browser info
      const sessionMetadata = {
        browser: navigator.userAgent,
        screen_width: window.screen.width,
        screen_height: window.screen.height,
        timestamp: new Date().toISOString()
      }

      const response = await fetch(`${API_URL}/feedback/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: 'demo_user', // TODO: Get from auth context
          rating: formData.rating,
          category: formData.category,
          comments: formData.comments || null,
          page_context: formData.pageContext,
          session_metadata: sessionMetadata
        })
      })

      const data = await response.json()

      if (response.ok) {
        setSubmitted(true)
        // Reset form
        setFormData({
          category: 'general',
          rating: 5,
          comments: '',
          pageContext: 'feedback-page'
        })
      } else {
        setError(data.detail?.message || 'Failed to submit feedback')
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Feedback submission error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-black text-white p-6 md:p-8 font-mono">
        <div className="max-w-2xl mx-auto">
          {/* Success Message */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="border border-white p-8 text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring' }}
              className="text-6xl mb-6"
            >
              ✓
            </motion.div>

            <div className="border-t border-b border-white py-6 mb-6">
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-xl mb-2"
              >
                Feedback received.
              </motion.p>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="text-lg text-gray-400"
              >
                Thank you for helping StudyQuest improve!
              </motion.p>
            </div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="space-y-4"
            >
              <button
                onClick={() => setSubmitted(false)}
                className="w-full border border-white px-6 py-3 hover:bg-white hover:text-black transition-colors"
              >
                SUBMIT_MORE_FEEDBACK()
              </button>

              <Link
                href="/"
                className="block w-full border border-gray-600 px-6 py-3 hover:bg-gray-900 transition-colors"
              >
                RETURN_TO_DASHBOARD()
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-8 font-mono">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white text-black px-6 py-4 mb-8"
        >
          <h1 className="text-2xl font-bold text-center">
            ═══════════ BETA FEEDBACK ═══════════
          </h1>
        </motion.div>

        {/* Intro */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="border border-gray-600 p-6 mb-8"
        >
          <h2 className="text-lg font-bold mb-3">// HELP_US_IMPROVE</h2>
          <p className="text-gray-400 text-sm mb-4">
            We're collecting feedback from beta testers to improve StudyQuest.
            Please share your thoughts on:
          </p>
          <ul className="text-sm text-gray-400 space-y-1 ml-4">
            <li>• UX clarity and design</li>
            <li>• Performance and speed</li>
            <li>• Content accuracy</li>
            <li>• Motivation and engagement</li>
          </ul>
        </motion.div>

        {/* Feedback Form */}
        <motion.form
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          onSubmit={handleSubmit}
          className="border border-white p-8 space-y-6"
        >
          {/* Category Selection */}
          <div>
            <label className="block text-sm mb-3 text-gray-400">
              // FEEDBACK_CATEGORY
            </label>
            <div className="space-y-2">
              {categories.map((cat) => (
                <label
                  key={cat.value}
                  className={`block border p-4 cursor-pointer transition-colors ${
                    formData.category === cat.value
                      ? 'border-white bg-gray-900'
                      : 'border-gray-700 hover:border-gray-500'
                  }`}
                >
                  <input
                    type="radio"
                    name="category"
                    value={cat.value}
                    checked={formData.category === cat.value}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="mr-3"
                  />
                  <span className="font-bold">{cat.label}</span>
                  <span className="text-sm text-gray-500 ml-2">— {cat.desc}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Rating */}
          <div>
            <label className="block text-sm mb-3 text-gray-400">
              // RATING (1 = Poor, 5 = Excellent)
            </label>
            <div className="flex gap-4 justify-center py-4 border border-gray-700 bg-black">
              {[1, 2, 3, 4, 5].map((num) => (
                <button
                  key={num}
                  type="button"
                  onClick={() => setFormData({ ...formData, rating: num })}
                  className={`w-16 h-16 border text-2xl font-bold transition-colors ${
                    formData.rating === num
                      ? 'border-white bg-white text-black'
                      : 'border-gray-600 hover:border-white'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
            <p className="text-xs text-center mt-2 text-gray-600">
              {formData.rating === 5 && 'Excellent'}
              {formData.rating === 4 && 'Good'}
              {formData.rating === 3 && 'Okay'}
              {formData.rating === 2 && 'Poor'}
              {formData.rating === 1 && 'Very Poor'}
            </p>
          </div>

          {/* Comments */}
          <div>
            <label className="block text-sm mb-3 text-gray-400">
              // COMMENTS (Optional)
            </label>
            <textarea
              value={formData.comments}
              onChange={(e) => setFormData({ ...formData, comments: e.target.value })}
              placeholder="Share your thoughts, suggestions, or issues encountered..."
              className="w-full bg-black border border-gray-600 text-white p-4 font-mono text-sm focus:border-white focus:outline-none resize-none"
              rows={6}
              maxLength={1000}
            />
            <p className="text-xs text-gray-600 mt-1">
              {formData.comments.length} / 1000 characters
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="border border-white p-4 bg-black"
            >
              <p className="text-sm">
                <span className="font-bold">[ERROR]</span> {error}
              </p>
            </motion.div>
          )}

          {/* Submit Button */}
          <div className="pt-4 border-t border-gray-700">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black px-6 py-4 font-bold text-lg hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'SUBMITTING...' : 'SUBMIT_FEEDBACK()'}
            </button>
          </div>

          {/* Back Link */}
          <Link
            href="/"
            className="block text-center text-sm text-gray-600 hover:text-white transition-colors"
          >
            ← BACK_TO_DASHBOARD
          </Link>
        </motion.form>
      </div>
    </div>
  )
}
