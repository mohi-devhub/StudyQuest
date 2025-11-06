'use client'

import { useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { useEffect, useState, Suspense } from 'react'

function ResultContent() {
  const searchParams = useSearchParams()
  const [mounted, setMounted] = useState(false)
  
  const score = Number(searchParams.get('score')) || 0
  const correct = Number(searchParams.get('correct')) || 0
  const total = Number(searchParams.get('total')) || 5
  const topic = searchParams.get('topic') || 'Quiz'

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
        <div className="text-6xl font-bold animate-pulse">LOADING...</div>
      </div>
    )
  }

  const getPerformanceLevel = () => {
    if (score >= 90) return { text: 'EXCELLENT!', color: 'text-green-400', emoji: '🎉' }
    if (score >= 70) return { text: 'GOOD JOB!', color: 'text-blue-400', emoji: '👍' }
    if (score >= 50) return { text: 'KEEP TRYING!', color: 'text-yellow-400', emoji: '💪' }
    return { text: 'STUDY MORE!', color: 'text-red-400', emoji: '📚' }
  }

  const performance = getPerformanceLevel()

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white">
      <div className="max-w-4xl mx-auto px-8 py-16">
        {/* Result Header */}
        <div className="text-center mb-12">
          <div className="text-terminal-gray text-sm mb-4">QUIZ_RESULT</div>
          <h1 className="text-4xl font-bold mb-2">{topic}</h1>
          <div className="text-terminal-gray">Quiz Completed</div>
        </div>

        {/* Score Display */}
        <div className="border-2 border-terminal-white p-12 mb-8 text-center">
          <div className="text-8xl font-bold mb-6">{score.toFixed(0)}%</div>
          <div className="text-3xl mb-4">
            {correct} / {total} Correct
          </div>
          <div className={`text-2xl ${performance.color} font-bold`}>
            {performance.emoji} {performance.text}
          </div>
        </div>

        {/* Performance Breakdown */}
        <div className="border border-terminal-white/30 p-8 mb-8">
          <h2 className="text-xl font-bold mb-6">PERFORMANCE_BREAKDOWN()</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-terminal-gray">Correct Answers:</span>
              <span className="font-mono text-green-400">{correct}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-terminal-gray">Incorrect Answers:</span>
              <span className="font-mono text-red-400">{total - correct}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-terminal-gray">Total Questions:</span>
              <span className="font-mono">{total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-terminal-gray">Success Rate:</span>
              <span className={`font-mono ${performance.color}`}>{score.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href={`/quiz?topic=${encodeURIComponent(topic)}`}
            className="px-8 py-6 border-2 border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors text-center font-bold"
          >
            ↻ RETRY_QUIZ()
          </Link>
          <Link
            href="/"
            className="px-8 py-6 border border-terminal-white/50 hover:border-terminal-white hover:bg-terminal-white/10 transition-colors text-center"
          >
            ← RETURN_HOME()
          </Link>
        </div>

        {/* Next Steps */}
        {score < 70 && (
          <div className="mt-8 p-6 border border-yellow-500/30 bg-yellow-500/5">
            <h3 className="text-yellow-400 font-bold mb-2">SUGGESTION:</h3>
            <p className="text-terminal-gray">
              Consider reviewing the study materials for {topic} and trying the quiz again to improve your understanding.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default function QuizResultPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
        <div className="text-6xl font-bold animate-pulse">LOADING...</div>
      </div>
    }>
      <ResultContent />
    </Suspense>
  )
}
