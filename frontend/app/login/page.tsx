'use client'

import { useState } from 'react'
import { useAuth } from '@/lib/useAuth'
import { useRouter } from 'next/navigation'
import { motion } from 'framer-motion'
import Link from 'next/link'
import ClientOnly from '@/components/ClientOnly'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { signIn } = useAuth()
  const router = useRouter()

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      await signIn(email, password)
      // Use replace instead of push to avoid back button issues
      // Redirect to root (dashboard) after successful login
      router.replace('/')
    } catch (err: any) {
      setError(err.message || 'Failed to sign in')
    } finally {
      setLoading(false)
    }
  }

  const fillTestCredentials = () => {
    setEmail('test@studyquest.dev')
    setPassword('testuser123')
  }

  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-sm text-gray-500 mb-2"
          >
            // AUTHENTICATION_SYSTEM
          </motion.div>
          <motion.h1
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-4xl font-bold mb-2"
          >
            StudyQuest
          </motion.h1>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-gray-400 text-sm"
          >
            Terminal-Style Learning Dashboard
          </motion.p>
        </div>

        {/* Login Form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="border border-white p-8"
        >
          <div className="text-sm text-gray-500 mb-6">// LOGIN</div>

          <ClientOnly>
            {error && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="border border-red-500 bg-red-950 bg-opacity-20 p-3 mb-6 text-sm"
              >
                <span className="text-red-500">ERROR:</span> {error}
              </motion.div>
            )}
          </ClientOnly>

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                EMAIL_ADDRESS
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-black border border-gray-600 px-4 py-3 focus:border-white focus:outline-none transition-colors font-mono"
                placeholder="user@example.com"
                required
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">
                PASSWORD
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-black border border-gray-600 px-4 py-3 focus:border-white focus:outline-none transition-colors font-mono"
                placeholder="••••••••"
                required
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-white text-black px-6 py-3 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-mono font-bold"
            >
              {loading ? 'AUTHENTICATING...' : 'LOGIN >'}
            </button>
          </form>

          <div className="mt-6 pt-6 border-t border-gray-800">
            <p className="text-sm text-gray-400 text-center mb-4">
              Don't have an account?
            </p>
            <Link
              href="/signup"
              className="block w-full border border-white px-6 py-3 hover:bg-white hover:text-black transition-colors text-center font-mono"
            >
              CREATE_ACCOUNT
            </Link>
          </div>
        </motion.div>

        {/* Test User Credentials */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-6 border border-gray-700 p-6 bg-gray-950"
        >
          <div className="text-xs text-gray-500 mb-3">// TEST_USER_CREDENTIALS</div>
          <div className="space-y-2 text-sm font-mono">
            <div className="flex justify-between">
              <span className="text-gray-400">Email:</span>
              <span className="text-white">test@studyquest.dev</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Password:</span>
              <span className="text-white">testuser123</span>
            </div>
          </div>
          <button
            onClick={fillTestCredentials}
            className="w-full mt-4 border border-gray-600 px-4 py-2 hover:border-white transition-colors text-xs"
          >
            AUTO-FILL_CREDENTIALS
          </button>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 text-center text-xs text-gray-600"
        >
          <p>StudyQuest v1.0 // Production Build</p>
          <p className="mt-1">Powered by Supabase Auth</p>
        </motion.div>
      </motion.div>
    </div>
  )
}
