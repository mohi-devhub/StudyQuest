'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '@/lib/useAuth'
import { supabase } from '@/lib/supabase'
import { createLogger } from '@/lib/logger'

const logger = createLogger('QuizPage')

interface QuizQuestion {
  question: string
  options: string[]
  answer: string
  explanation: string
}

interface SavedSession {
  id: string
  topic: string
  summary: string
  key_points: string[]
  quiz_questions: QuizQuestion[]
  created_at: string
}

type QuizMode = 'select' | 'saved' | 'upload' | 'topic' | 'quiz'

export default function QuizPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  
  const [mode, setMode] = useState<QuizMode>('select')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedSessions, setSavedSessions] = useState<SavedSession[]>([])
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [customTopic, setCustomTopic] = useState('')
  const [quizData, setQuizData] = useState<{
    topic: string
    quiz: QuizQuestion[]
    summary?: string
    key_points?: string[]
  } | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: string }>({})

  useEffect(() => {
    // Only redirect if auth check is complete and user is not logged in
    if (!authLoading && !user) {
      router.push('/login')
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (mode === 'saved') {
      fetchSavedSessions()
    }
  }, [mode])

  const fetchSavedSessions = async () => {
    try {
      setLoading(true)
      setError(null)
      const { data, error: fetchError } = await supabase
        .from('study_sessions')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(10)

      if (fetchError) throw fetchError
      setSavedSessions(data || [])
    } catch (err) {
      logger.error('Error fetching sessions', { userId: user?.id, error: String(err) })
      setError('Failed to load saved sessions. Make sure the study_sessions table migration has been run.')
    } finally {
      setLoading(false)
    }
  }

  const generateQuizFromSaved = async (session: SavedSession) => {
    try {
      setLoading(true)
      setError(null)

      // Use existing quiz questions if available
      if (session.quiz_questions && session.quiz_questions.length > 0) {
        setQuizData({
          topic: session.topic,
          summary: session.summary,
          key_points: session.key_points,
          quiz: session.quiz_questions
        })
        setMode('quiz')
        setLoading(false)
        return
      }

      // Otherwise generate new quiz from the notes
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/quiz/generate-from-topic`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id}`
        },
        body: JSON.stringify({
          topic: session.topic,
          summary: session.summary,
          key_points: session.key_points,
          num_questions: 5,
          use_cache: true
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Failed to generate quiz')
      }

      const data = await response.json()
      setQuizData({
        topic: session.topic,
        summary: session.summary,
        key_points: session.key_points,
        quiz: data.questions || []
      })
      setMode('quiz')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate quiz')
    } finally {
      setLoading(false)
    }
  }

  const generateQuizFromPDF = async () => {
    if (!selectedFile) return

    try {
      setLoading(true)
      setError(null)

      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('num_questions', '5')

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/quiz/generate-from-pdf`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user?.id}`
        },
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Failed to process PDF')
      }

      const data = await response.json()
      setQuizData({
        topic: `Quiz from ${selectedFile.name}`,
        quiz: data.questions || []
      })
      setMode('quiz')
      setSelectedFile(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate quiz from PDF')
    } finally {
      setLoading(false)
    }
  }

  const generateQuizFromTopic = async () => {
    if (!customTopic.trim()) return

    try {
      setLoading(true)
      setError(null)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const response = await fetch(`${apiUrl}/quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user?.id}`
        },
        body: JSON.stringify({
          topic: customTopic.trim(),
          num_questions: 5,
          difficulty: 'medium',
          user_id: user?.id || 'anonymous',
          use_cache: true
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Failed to generate quiz')
      }

      const data = await response.json()
      setQuizData({
        topic: customTopic.trim(),
        quiz: data.quiz || []
      })
      setMode('quiz')
      setCustomTopic('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate quiz')
    } finally {
      setLoading(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type !== 'application/pdf') {
        setError('Please select a PDF file')
        return
      }
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB')
        return
      }
      setSelectedFile(file)
      setError(null)
    }
  }

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer
    })
  }

  const handleNext = () => {
    if (quizData && currentQuestion < quizData.quiz.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = () => {
    if (!quizData) return

    let correctCount = 0
    quizData.quiz.forEach((q, index) => {
      if (selectedAnswers[index] === q.answer) {
        correctCount++
      }
    })

    const score = (correctCount / quizData.quiz.length) * 100
    router.push(`/quiz/result?score=${score}&correct=${correctCount}&total=${quizData.quiz.length}&topic=${encodeURIComponent(quizData.topic)}`)
  }

  const isAnswered = (questionIndex: number) => {
    return selectedAnswers[questionIndex] !== undefined
  }

  const allAnswered = quizData?.quiz.every((_, index) => isAnswered(index)) || false

  if (mode === 'select') {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white">
        <div className="border-b border-terminal-white/20">
          <div className="max-w-6xl mx-auto px-8 py-8">
            <h1 className="text-4xl font-bold mb-2">QUIZ_GENERATOR()</h1>
            <p className="text-terminal-gray">Select how you want to generate your quiz</p>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-8 py-12">
          {error && (
            <div className="mb-8 p-4 border border-red-500 bg-red-500/10 text-red-400">
              {error}
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('saved')}
              className="p-8 border-2 border-terminal-white/30 hover:border-terminal-white transition-all text-left group"
            >
              <div className="text-2xl font-bold mb-4 group-hover:text-terminal-green transition-colors">
                📚 FROM_SAVED_NOTES()
              </div>
              <p className="text-terminal-gray mb-4">
                Select from your previously generated AI study materials
              </p>
              <div className="text-sm text-terminal-gray/70">
                • Quick access to saved topics<br/>
                • Uses existing study notes<br/>
                • Instant quiz generation
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('upload')}
              className="p-8 border-2 border-terminal-white/30 hover:border-terminal-white transition-all text-left group"
            >
              <div className="text-2xl font-bold mb-4 group-hover:text-terminal-green transition-colors">
                📄 UPLOAD_PDF()
              </div>
              <p className="text-terminal-gray mb-4">
                Upload a PDF document and generate quiz questions from it
              </p>
              <div className="text-sm text-terminal-gray/70">
                • Max 10MB file size<br/>
                • Text-based PDFs only<br/>
                • AI extracts content
              </div>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setMode('topic')}
              className="p-8 border-2 border-terminal-white/30 hover:border-terminal-white transition-all text-left group"
            >
              <div className="text-2xl font-bold mb-4 group-hover:text-terminal-green transition-colors">
                ✍️ CUSTOM_TOPIC()
              </div>
              <p className="text-terminal-gray mb-4">
                Enter any topic and let AI generate quiz questions
              </p>
              <div className="text-sm text-terminal-gray/70">
                • Any topic you want<br/>
                • AI generates fresh content<br/>
                • Instant quiz creation
              </div>
            </motion.button>
          </div>
        </div>
      </div>
    )
  }

  if (mode === 'saved') {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white">
        <div className="border-b border-terminal-white/20">
          <div className="max-w-6xl mx-auto px-8 py-8">
            <button
              onClick={() => setMode('select')}
              className="text-terminal-gray hover:text-terminal-white mb-4 transition-colors"
            >
              ← BACK
            </button>
            <h1 className="text-4xl font-bold mb-2">FROM_SAVED_NOTES()</h1>
            <p className="text-terminal-gray">Select a previously generated study session</p>
          </div>
        </div>

        <div className="max-w-6xl mx-auto px-8 py-12">
          {loading && (
            <div className="text-center py-12">
              <div className="text-2xl font-bold animate-pulse">LOADING...</div>
            </div>
          )}

          {error && (
            <div className="mb-8 p-4 border border-red-500 bg-red-500/10 text-red-400">
              {error}
            </div>
          )}

          {!loading && savedSessions.length === 0 && (
            <div className="text-center py-12">
              <div className="text-2xl font-bold mb-4">NO_SAVED_SESSIONS</div>
              <p className="text-terminal-gray mb-8">
                You haven't created any study sessions yet.<br/>
                Go to the Study page to generate some notes first.
              </p>
              <button
                onClick={() => router.push('/study')}
                className="px-8 py-4 border border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors"
              >
                GO_TO_STUDY()
              </button>
            </div>
          )}

          {!loading && savedSessions.length > 0 && (
            <div className="space-y-4">
              {savedSessions.map((session) => (
                <motion.button
                  key={session.id}
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => generateQuizFromSaved(session)}
                  className="w-full p-6 border border-terminal-white/30 hover:border-terminal-white transition-all text-left"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="text-xl font-bold mb-2">{session.topic}</div>
                      <p className="text-terminal-gray text-sm mb-3 line-clamp-2">
                        {session.summary}
                      </p>
                      <div className="text-xs text-terminal-gray/70">
                        {new Date(session.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </div>
                    </div>
                    <div className="ml-4 text-terminal-green">→</div>
                  </div>
                </motion.button>
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  if (mode === 'upload') {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white">
        <div className="border-b border-terminal-white/20">
          <div className="max-w-6xl mx-auto px-8 py-8">
            <button
              onClick={() => setMode('select')}
              className="text-terminal-gray hover:text-terminal-white mb-4 transition-colors"
            >
              ← BACK
            </button>
            <h1 className="text-4xl font-bold mb-2">UPLOAD_PDF()</h1>
            <p className="text-terminal-gray">Upload a PDF document to generate quiz questions</p>
          </div>
        </div>

        <div className="max-w-3xl mx-auto px-8 py-12">
          {error && (
            <div className="mb-8 p-4 border border-red-500 bg-red-500/10 text-red-400">
              {error}
            </div>
          )}

          <div className="border-2 border-dashed border-terminal-white/30 p-12 text-center">
            <div className="text-6xl mb-6">📄</div>
            <input
              type="file"
              accept=".pdf,application/pdf"
              onChange={handleFileSelect}
              className="hidden"
              id="pdf-upload"
            />
            <label
              htmlFor="pdf-upload"
              className="inline-block px-8 py-4 border border-terminal-white hover:bg-terminal-white hover:text-terminal-black cursor-pointer transition-colors"
            >
              SELECT_PDF_FILE()
            </label>
            <p className="text-terminal-gray mt-4 text-sm">
              Maximum file size: 10MB • PDF files only
            </p>
          </div>

          {selectedFile && (
            <div className="mt-8 p-6 border border-terminal-white/30">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <div className="font-bold">{selectedFile.name}</div>
                  <div className="text-sm text-terminal-gray">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-terminal-gray hover:text-red-400 transition-colors"
                >
                  ✕
                </button>
              </div>
              <button
                onClick={generateQuizFromPDF}
                disabled={loading}
                className="w-full px-8 py-4 border-2 border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-bold"
              >
                {loading ? 'PROCESSING...' : 'GENERATE_QUIZ()'}
              </button>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (mode === 'topic') {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white">
        <div className="border-b border-terminal-white/20">
          <div className="max-w-6xl mx-auto px-8 py-8">
            <button
              onClick={() => setMode('select')}
              className="text-terminal-gray hover:text-terminal-white mb-4 transition-colors"
            >
              ← BACK
            </button>
            <h1 className="text-4xl font-bold mb-2">CUSTOM_TOPIC()</h1>
            <p className="text-terminal-gray">Enter any topic to generate quiz questions</p>
          </div>
        </div>

        <div className="max-w-3xl mx-auto px-8 py-12">
          {error && (
            <div className="mb-8 p-4 border border-red-500 bg-red-500/10 text-red-400">
              {error}
            </div>
          )}

          <div className="mb-8">
            <label className="block text-sm text-terminal-gray mb-2">TOPIC_NAME</label>
            <input
              type="text"
              value={customTopic}
              onChange={(e) => setCustomTopic(e.target.value.slice(0, 50))}
              onKeyPress={(e) => e.key === 'Enter' && customTopic.trim() && generateQuizFromTopic()}
              placeholder="e.g., Python Functions, World War II, Photosynthesis"
              className="w-full px-4 py-3 bg-terminal-black border border-terminal-white/30 text-terminal-white focus:border-terminal-white outline-none transition-colors"
              maxLength={50}
            />
            <div className="text-right text-xs text-terminal-gray mt-1">
              {customTopic.length}/50
            </div>
          </div>

          <button
            onClick={generateQuizFromTopic}
            disabled={!customTopic.trim() || loading}
            className="w-full px-8 py-4 border-2 border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors disabled:opacity-30 disabled:cursor-not-allowed font-bold"
          >
            {loading ? 'GENERATING...' : 'GENERATE_QUIZ()'}
          </button>

          <div className="mt-8 p-4 border border-terminal-white/20 text-sm text-terminal-gray">
            <div className="font-bold mb-2">EXAMPLES:</div>
            <div className="space-y-1">
              • JavaScript Promises<br/>
              • Quantum Physics Basics<br/>
              • Ancient Roman History<br/>
              • Machine Learning Algorithms
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (mode === 'quiz' && quizData) {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white">
        <div className="border-b border-terminal-white/20">
          <div className="max-w-5xl mx-auto px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-terminal-gray text-xs mb-2">QUIZ_SESSION</div>
                <h1 className="text-3xl font-bold">{quizData.topic}</h1>
              </div>
              <div className="text-right">
                <div className="text-terminal-gray text-xs mb-2">PROGRESS</div>
                <div className="text-2xl font-bold">
                  {currentQuestion + 1} / {quizData.quiz.length}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-5xl mx-auto px-8 py-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentQuestion}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.15 }}
            >
              <div className="mb-8">
                <div className="text-terminal-gray text-xs mb-2">QUESTION_{currentQuestion + 1}</div>
                <div className="text-2xl font-bold leading-relaxed">
                  {quizData.quiz[currentQuestion].question}
                </div>
              </div>

              <div className="space-y-4 mb-12">
                {quizData.quiz[currentQuestion].options.map((option, index) => {
                  const optionLetter = option.charAt(0)
                  const isSelected = selectedAnswers[currentQuestion] === optionLetter
                  
                  return (
                    <motion.button
                      key={index}
                      whileHover={{ scale: 1.01 }}
                      whileTap={{ scale: 0.99 }}
                      onClick={() => handleAnswerSelect(currentQuestion, optionLetter)}
                      className={`w-full text-left p-6 border-2 transition-all ${
                        isSelected
                          ? 'border-terminal-white bg-terminal-white/10'
                          : 'border-terminal-white/30 hover:border-terminal-white/60'
                      }`}
                    >
                      <div className="flex items-start">
                        <div className={`w-6 h-6 border-2 border-terminal-white mr-4 mt-1 flex items-center justify-center ${
                          isSelected ? 'bg-terminal-white' : ''
                        }`}>
                          {isSelected && (
                            <div className="w-3 h-3 bg-terminal-black"></div>
                          )}
                        </div>
                        <div className="flex-1 font-mono">{option}</div>
                      </div>
                    </motion.button>
                  )
                })}
              </div>

              <div className="flex items-center justify-center space-x-2 mb-8">
                {quizData.quiz.map((_, index) => (
                  <div
                    key={index}
                    className={`w-3 h-3 border border-terminal-white ${
                      isAnswered(index) ? 'bg-terminal-white' : ''
                    } ${index === currentQuestion ? 'scale-125' : ''} transition-all`}
                  />
                ))}
              </div>
            </motion.div>
          </AnimatePresence>

          <div className="flex items-center justify-between pt-8 border-t border-terminal-white/20">
            <button
              onClick={handlePrevious}
              disabled={currentQuestion === 0}
              className={`px-8 py-4 border border-terminal-white transition-all ${
                currentQuestion === 0
                  ? 'opacity-30 cursor-not-allowed'
                  : 'hover:bg-terminal-white hover:text-terminal-black'
              }`}
            >
              ← PREVIOUS
            </button>

            <div className="text-terminal-gray text-sm">
              {Object.keys(selectedAnswers).length} / {quizData.quiz.length} answered
            </div>

            {currentQuestion < quizData.quiz.length - 1 ? (
              <button
                onClick={handleNext}
                disabled={!isAnswered(currentQuestion)}
                className={`px-8 py-4 border border-terminal-white transition-all ${
                  !isAnswered(currentQuestion)
                    ? 'opacity-30 cursor-not-allowed'
                    : 'hover:bg-terminal-white hover:text-terminal-black'
                }`}
              >
                NEXT →
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!allAnswered}
                className={`px-8 py-4 border-2 border-terminal-white transition-all ${
                  !allAnswered
                    ? 'opacity-30 cursor-not-allowed'
                    : 'hover:bg-terminal-white hover:text-terminal-black font-bold'
                }`}
              >
                SUBMIT_QUIZ() →
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
      <div className="text-6xl font-bold animate-pulse">LOADING...</div>
    </div>
  )
}
