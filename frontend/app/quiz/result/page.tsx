"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useEffect, useState, Suspense } from "react";
import { useAuth } from "@/lib/useAuth";
import { supabase } from "@/lib/supabase";

interface QuizQuestion {
  question: string;
  options: string[];
  correctAnswer: string;
  userAnswer?: string;
  explanation?: string;
}

interface QuizResults {
  topic: string;
  score: number;
  correct: number;
  total: number;
  questions: QuizQuestion[];
}

function ResultContent() {
  const searchParams = useSearchParams();
  const { user } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [quizResults, setQuizResults] = useState<QuizResults | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [xpEarned, setXpEarned] = useState<number | null>(null);

  const score = Number(searchParams.get("score")) || 0;
  const correct = Number(searchParams.get("correct")) || 0;
  const total = Number(searchParams.get("total")) || 5;
  const topic = searchParams.get("topic") || "Quiz";

  useEffect(() => {
    setMounted(true);
    
    // Load quiz results from sessionStorage
    const stored = sessionStorage.getItem('quizResults');
    if (stored) {
      setQuizResults(JSON.parse(stored));
    }
  }, []);

  useEffect(() => {
    // Submit quiz to backend
    const submitQuiz = async () => {
      if (!user?.id || submitting || xpEarned !== null) return;
      
      setSubmitting(true);
      try {
        // Get the Supabase session token
        const { data: { session } } = await supabase.auth.getSession();
        const token = session?.access_token;
        
        if (!token) {
          console.error('No auth token available');
          return;
        }
        
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/progress/v2/submit-quiz`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            user_id: user.id,
            topic: topic,
            correct: correct,
            total: total,
            difficulty: 'medium',
            time_taken: 0
          })
        });

        if (response.ok) {
          const data = await response.json();
          setXpEarned(data.xp_earned || 0);
        } else {
          console.error('Quiz submission failed:', response.status, await response.text());
        }
      } catch (error) {
        console.error('Failed to submit quiz:', error);
      } finally {
        setSubmitting(false);
      }
    };

    if (mounted && user?.id) {
      submitQuiz();
    }
  }, [mounted, user, topic, correct, total, submitting, xpEarned]);

  if (!mounted) {
    return (
      <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
        <div className="text-6xl font-bold animate-pulse">LOADING...</div>
      </div>
    );
  }

  const getPerformanceLevel = () => {
    if (score >= 90)
      return { text: "EXCELLENT!", color: "text-green-400", emoji: "🎉" };
    if (score >= 70)
      return { text: "GOOD JOB!", color: "text-blue-400", emoji: "👍" };
    if (score >= 50)
      return { text: "KEEP TRYING!", color: "text-yellow-400", emoji: "💪" };
    return { text: "STUDY MORE!", color: "text-red-400", emoji: "📚" };
  };

  const performance = getPerformanceLevel();

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
              <span className={`font-mono ${performance.color}`}>
                {score.toFixed(1)}%
              </span>
            </div>
            {xpEarned !== null && (
              <div className="flex justify-between pt-4 border-t border-terminal-white/20">
                <span className="text-terminal-gray">XP Earned:</span>
                <span className="font-mono text-terminal-green">+{xpEarned} XP</span>
              </div>
            )}
          </div>
        </div>

        {/* Question Review */}
        {quizResults && quizResults.questions.length > 0 && (
          <div className="border border-terminal-white/30 p-8 mb-8">
            <h2 className="text-xl font-bold mb-6">QUESTION_REVIEW()</h2>
            <div className="space-y-6">
              {quizResults.questions.map((q, index) => {
                const isCorrect = q.userAnswer === q.correctAnswer;
                const wasAnswered = q.userAnswer !== undefined;
                
                return (
                  <div key={index} className={`p-4 border ${isCorrect ? 'border-green-500/30 bg-green-500/5' : 'border-red-500/30 bg-red-500/5'}`}>
                    <div className="flex items-start gap-3 mb-3">
                      <span className={`font-mono ${isCorrect ? 'text-green-400' : 'text-red-400'}`}>
                        {isCorrect ? '✓' : '✗'}
                      </span>
                      <div className="flex-1">
                        <div className="font-bold mb-2">Q{index + 1}: {q.question}</div>
                        
                        {/* Options */}
                        <div className="space-y-2 mb-3">
                          {q.options.map((option, optIndex) => {
                            const letter = String.fromCharCode(65 + optIndex);
                            const isCorrectOption = letter === q.correctAnswer;
                            const isUserAnswer = letter === q.userAnswer;
                            
                            return (
                              <div key={optIndex} className={`flex items-center gap-2 text-sm ${
                                isCorrectOption ? 'text-green-400 font-bold' : 
                                isUserAnswer && !isCorrect ? 'text-red-400' : 
                                'text-terminal-gray'
                              }`}>
                                <span className="font-mono">{letter}.</span>
                                <span>{option}</span>
                                {isCorrectOption && <span className="ml-2">✓ Correct</span>}
                                {isUserAnswer && !isCorrect && <span className="ml-2">✗ Your answer</span>}
                              </div>
                            );
                          })}
                        </div>

                        {/* Result */}
                        {!wasAnswered ? (
                          <div className="text-yellow-400 text-sm">Not answered</div>
                        ) : isCorrect ? (
                          <div className="text-green-400 text-sm">✓ Correct!</div>
                        ) : (
                          <div className="text-red-400 text-sm">
                            ✗ Wrong. Correct answer: {q.correctAnswer}
                          </div>
                        )}

                        {/* Explanation */}
                        {q.explanation && !isCorrect && (
                          <div className="mt-3 p-3 bg-terminal-white/5 border-l-2 border-blue-400">
                            <div className="text-blue-400 text-xs font-bold mb-1">EXPLANATION:</div>
                            <div className="text-terminal-gray text-sm">{q.explanation}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

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
              Consider reviewing the study materials for {topic} and trying the
              quiz again to improve your understanding.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default function QuizResultPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-terminal-black text-terminal-white flex items-center justify-center">
          <div className="text-6xl font-bold animate-pulse">LOADING...</div>
        </div>
      }
    >
      <ResultContent />
    </Suspense>
  );
}
