'use client'

import { useEffect, useState, Suspense } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'

interface QuizQuestion {
  question: string
  options: string[]
  answer: string
  explanation: string
}

interface StudyPackage {
  topic: string
  notes: {
    topic: string
    summary: string
    key_points: string[]
  }
  quiz: QuizQuestion[]
}

function QuizContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const topic = searchParams.get('topic') || 'General Knowledge'
  const difficulty = searchParams.get('difficulty') || 'medium'

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [studyPackage, setStudyPackage] = useState<StudyPackage | null>(null)
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: string }>({})
  const [showNotes, setShowNotes] = useState(true)

  useEffect(() => {
    fetchQuiz()
  }, [topic])

  const fetchQuiz = async () => {
    try {
      setLoading(true)
      setError(null)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      
      // For demo, use mock data
      // In production, uncomment the API call below
      
      // const response = await fetch(`${apiUrl}/study`, {
      //   method: 'POST',
      //   headers: {
      //     'Content-Type': 'application/json',
      //     'Authorization': `Bearer ${token}` // Add auth token
      //   },
      //   body: JSON.stringify({
      //     topic: topic,
      //     num_questions: 5
      //   })
      // })
      // const data = await response.json()
      // setStudyPackage(data)

      // Mock data for demonstration
      await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay

      const mockPackage: StudyPackage = {
        topic: topic,
        notes: {
          topic: topic,
          summary: `${topic} is a fundamental concept in computer science and software development. Understanding this topic will help you build better applications and solve complex problems efficiently.`,
          key_points: [
            'Core concepts and principles',
            'Best practices and patterns',
            'Common use cases and applications',
            'Performance considerations',
            'Advanced techniques and optimizations'
          ]
        },
        quiz: [
          {
            question: `What is the primary purpose of ${topic}?`,
            options: [
              'A) To increase code complexity',
              'B) To solve specific computational problems efficiently',
              'C) To make code harder to read',
              'D) To reduce application performance'
            ],
            answer: 'B',
            explanation: `${topic} is designed to solve computational problems efficiently and effectively.`
          },
          {
            question: `Which of the following is a key benefit of understanding ${topic}?`,
            options: [
              'A) Better problem-solving skills',
              'B) Slower development process',
              'C) More bugs in code',
              'D) Reduced code quality'
            ],
            answer: 'A',
            explanation: 'Understanding core concepts improves your ability to solve problems effectively.'
          },
          {
            question: `In the context of ${topic}, what should developers prioritize?`,
            options: [
              'A) Writing code as fast as possible',
              'B) Understanding fundamentals before implementation',
              'C) Ignoring best practices',
              'D) Copying code without understanding'
            ],
            answer: 'B',
            explanation: 'Solid fundamentals are crucial for effective implementation.'
          },
          {
            question: `How does ${topic} relate to real-world applications?`,
            options: [
              'A) It has no practical use',
              'B) Only useful in theoretical contexts',
              'C) Applied in many production systems and applications',
              'D) Only for academic purposes'
            ],
            answer: 'C',
            explanation: 'Most concepts are widely applied in real-world production systems.'
          },
          {
            question: `What is the recommended approach when learning ${topic}?`,
            options: [
              'A) Skip the basics and jump to advanced topics',
              'B) Build understanding progressively from fundamentals',
              'C) Only memorize without understanding',
              'D) Avoid practical exercises'
            ],
            answer: 'B',
            explanation: 'Progressive learning from fundamentals ensures solid understanding.'
          }
        ]
      }

      setStudyPackage(mockPackage)
      setLoading(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load quiz')
      setLoading(false)
    }
  }

  const handleAnswerSelect = (questionIndex: number, answer: string) => {
    setSelectedAnswers({
      ...selectedAnswers,
      [questionIndex]: answer
    })
  }

  const handleNext = () => {
    if (studyPackage && currentQuestion < studyPackage.quiz.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const handleSubmit = async () => {
    if (!studyPackage) return

    // Calculate score
    let correctCount = 0
    studyPackage.quiz.forEach((q, index) => {
      if (selectedAnswers[index] === q.answer) {
        correctCount++
      }
    })

    const score = (correctCount / studyPackage.quiz.length) * 100

    // For demo, redirect directly to result page
    // In production, submit to backend first
    router.push(`/quiz/result?score=${score}&correct=${correctCount}&total=${studyPackage.quiz.length}&topic=${encodeURIComponent(topic)}`)
  }

  const isAnswered = (questionIndex: number) => {
    return selectedAnswers[questionIndex] !== undefined
  }

  const allAnswered = studyPackage?.quiz.every((_, index) => isAnswered(index)) || false

  if (loading) {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl font-bold mb-4 animate-pulse">LOADING...</div>
          <div className="text-terminal-gray">Generating quiz questions</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
        <div className="max-w-2xl mx-auto text-center p-8 border border-terminal-white">
          <div className="text-4xl font-bold mb-4">ERROR</div>
          <div className="text-terminal-gray mb-8">{error}</div>
          <Link 
            href="/"
            className="inline-block px-8 py-4 border border-terminal-white hover:bg-terminal-white hover:text-terminal-black transition-colors"
          >
            RETURN_HOME()
          </Link>
        </div>
      </div>
    )
  }

  if (!studyPackage) return null

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white">
      {/* Header */}
      <div className="border-b border-terminal-white/20">
        <div className="max-w-5xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-terminal-gray text-xs mb-2">QUIZ_SESSION</div>
              <h1 className="text-3xl font-bold">{topic}</h1>
              <div className="text-terminal-gray text-sm mt-1">
                Difficulty: {difficulty.toUpperCase()}
              </div>
            </div>
            <div className="text-right">
              <div className="text-terminal-gray text-xs mb-2">PROGRESS</div>
              <div className="text-2xl font-bold">
                {currentQuestion + 1} / {studyPackage.quiz.length}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Study Notes Section */}
      {showNotes && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="border-b border-terminal-white/20 bg-terminal-white/5"
        >
          <div className="max-w-5xl mx-auto px-8 py-8">
            <div className="flex items-start justify-between mb-4">
              <h2 className="text-xl font-bold">STUDY_NOTES()</h2>
              <button
                onClick={() => setShowNotes(false)}
                className="text-terminal-gray hover:text-terminal-white transition-colors"
              >
                [HIDE]
              </button>
            </div>
            <p className="text-terminal-gray mb-6">{studyPackage.notes.summary}</p>
            <div className="space-y-2">
              {studyPackage.notes.key_points.map((point, index) => (
                <div key={index} className="flex items-start">
                  <span className="text-terminal-gray mr-3">{index + 1}.</span>
                  <span>{point}</span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {!showNotes && (
        <div className="border-b border-terminal-white/20">
          <div className="max-w-5xl mx-auto px-8 py-4">
            <button
              onClick={() => setShowNotes(true)}
              className="text-terminal-gray hover:text-terminal-white transition-colors text-sm"
            >
              [SHOW_NOTES]
            </button>
          </div>
        </div>
      )}

      {/* Quiz Question */}
      <div className="max-w-5xl mx-auto px-8 py-12">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentQuestion}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.15 }}
          >
            {/* Question */}
            <div className="mb-8">
              <div className="text-terminal-gray text-xs mb-2">QUESTION_{currentQuestion + 1}</div>
              <div className="text-2xl font-bold leading-relaxed">
                {studyPackage.quiz[currentQuestion].question}
              </div>
            </div>

            {/* Options */}
            <div className="space-y-4 mb-12">
              {studyPackage.quiz[currentQuestion].options.map((option, index) => {
                const optionLetter = option.charAt(0) // A), B), C), D)
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

            {/* Answer Progress Indicator */}
            <div className="flex items-center justify-center space-x-2 mb-8">
              {studyPackage.quiz.map((_, index) => (
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

        {/* Navigation */}
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
            {Object.keys(selectedAnswers).length} / {studyPackage.quiz.length} answered
          </div>

          {currentQuestion < studyPackage.quiz.length - 1 ? (
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

export default function QuizPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
        <div className="text-6xl font-bold animate-pulse">LOADING...</div>
      </div>
    }>
      <QuizContent />
    </Suspense>
  )
}
