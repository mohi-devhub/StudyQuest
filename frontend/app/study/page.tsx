"use client";

import { useState, useEffect, Suspense } from "react";
import { motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import { supabase } from "@/lib/supabase";
import { createLogger } from "@/lib/logger";

const logger = createLogger("StudyPage");

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface StudyNotes {
  summary: string;
  key_points: string[];
  examples: string[];
  tips: string[];
}

function StudyPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { userId } = useAuth();
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState<StudyNotes | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generationTime, setGenerationTime] = useState<number | null>(null);
  const [autoStarted, setAutoStarted] = useState(false);

  // Auto-generate notes if coming from recommendations
  useEffect(() => {
    const topicParam = searchParams.get('topic');
    const autoStart = searchParams.get('autoStart');
    const difficulty = searchParams.get('difficulty');
    
    if (autoStart === 'true' && topicParam && !autoStarted && !loading) {
      setTopic(topicParam);
      setAutoStarted(true);
      // Trigger generation automatically
      setTimeout(() => {
        const formEvent = { preventDefault: () => {} } as React.FormEvent;
        handleGenerate(formEvent);
      }, 100);
    } else if (topicParam && !topic) {
      setTopic(topicParam);
    }
  }, [searchParams, autoStarted, loading]);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!topic.trim()) {
      setError("Please enter a topic");
      return;
    }

    if (topic.length > 50) {
      setError("Topic must be 50 characters or less");
      return;
    }

    setLoading(true);
    setError(null);
    setNotes(null);

    const startTime = Date.now();

    try {
      // Get the session token
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (!session?.access_token) {
        setError("Authentication required. Please log in again.");
        return;
      }

      const response = await fetch(`${API_URL}/study`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({
          topic: topic.trim(),
          user_id: userId,
          use_cache: true,
        }),
      });

      const endTime = Date.now();
      setGenerationTime((endTime - startTime) / 1000);

      const data = await response.json();

      if (response.ok) {
        setNotes(data.notes);

        // Save study session to database for later use in quiz
        if (userId && data.notes) {
          try {
            await supabase.from("study_sessions").insert({
              user_id: userId,
              topic: topic.trim(),
              summary: data.notes.summary,
              key_points: data.notes.key_points || [],
              quiz_questions: data.quiz || [],
            });
          } catch (saveErr) {
            logger.warn("Failed to save study session", {
              userId,
              topic,
              error: String(saveErr),
            });
            // Don't show error to user, this is optional
          }
        }
      } else {
        setError(data.detail?.message || "Failed to generate study notes");
      }
    } catch (err) {
      setError("Network error. Please check if backend is running.");
      logger.error("Study generation error", {
        userId,
        topic,
        error: String(err),
      });
    } finally {
      setLoading(false);
    }
  };

  const handleTakeQuiz = () => {
    router.push(`/quiz?topic=${encodeURIComponent(topic)}`);
  };

  return (
    <div className="min-h-screen bg-black text-white p-6 md:p-8 font-mono">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4"
        >
          <button
            onClick={() => router.push('/')}
            className="text-gray-400 hover:text-white transition-colors text-sm"
          >
            ← BACK_TO_DASHBOARD
          </button>
        </motion.div>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white text-black px-6 py-4 mb-8"
        >
          <h1 className="text-2xl font-bold text-center">
            ════════ STUDY SESSION ════════
          </h1>
        </motion.div>

        {/* Topic Input Form */}
        <motion.form
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          onSubmit={handleGenerate}
          className="border border-white p-6 mb-8"
        >
          <label className="block text-sm text-gray-400 mb-3">
            // ENTER_TOPIC
          </label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Python Functions, World War II, Photosynthesis"
            className="w-full bg-black border border-gray-600 text-white px-4 py-3 font-mono focus:border-white focus:outline-none mb-4"
            maxLength={50}
            disabled={loading}
          />

          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-600">
              {topic.length}/50 characters
            </span>
            <button
              type="submit"
              disabled={loading || !topic.trim()}
              className="bg-white text-black px-6 py-3 font-bold hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "GENERATING..." : "GENERATE_NOTES()"}
            </button>
          </div>
        </motion.form>

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="border border-gray-600 p-8 text-center"
          >
            <div className="animate-pulse space-y-4">
              <div className="text-2xl">⚡</div>
              <p>Generating study notes...</p>
              <p className="text-sm text-gray-500">
                Using AI to analyze "{topic}"
              </p>
            </div>
          </motion.div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="border border-white p-6 bg-black"
          >
            <p className="text-sm">
              <span className="font-bold">[ERROR]</span> {error}
            </p>
          </motion.div>
        )}

        {/* Study Notes Display */}
        {notes && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Generation Time */}
            {generationTime && (
              <div className="border border-gray-700 p-4 text-sm text-gray-400">
                <span className="font-bold">Generation Time:</span>{" "}
                {generationTime.toFixed(2)}s
                {generationTime < 10 ? " ✓" : " ⚠️ (slower than expected)"}
              </div>
            )}

            {/* Summary */}
            <div className="border border-white p-6">
              <h2 className="text-xl font-bold mb-4">// SUMMARY</h2>
              <p className="text-gray-300 leading-relaxed">{notes.summary}</p>
            </div>

            {/* Key Points */}
            {notes.key_points && notes.key_points.length > 0 && (
              <div className="border border-white p-6">
                <h2 className="text-xl font-bold mb-4">// KEY_POINTS</h2>
                <ul className="space-y-3">
                  {notes.key_points.map((point, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.1 + index * 0.05 }}
                      className="flex gap-3"
                    >
                      <span className="text-gray-600 flex-shrink-0">
                        [{index + 1}]
                      </span>
                      <span className="text-gray-300">{point}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>
            )}

            {/* Examples */}
            {notes.examples && notes.examples.length > 0 && (
              <div className="border border-gray-700 p-6">
                <h2 className="text-lg font-bold mb-4">// EXAMPLES</h2>
                <div className="space-y-4">
                  {notes.examples.map((example, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.2 + index * 0.05 }}
                      className="border border-gray-700 p-4 bg-gray-900"
                    >
                      <span className="text-sm text-gray-500">
                        Example {index + 1}:
                      </span>
                      <p className="text-gray-300 mt-2">{example}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* Tips */}
            {notes.tips && notes.tips.length > 0 && (
              <div className="border border-gray-700 p-6">
                <h2 className="text-lg font-bold mb-4">// STUDY_TIPS</h2>
                <ul className="space-y-2">
                  {notes.tips.map((tip, index) => (
                    <motion.li
                      key={index}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 + index * 0.05 }}
                      className="text-sm text-gray-400"
                    >
                      💡 {tip}
                    </motion.li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            <div className="border-t border-gray-700 pt-6 space-y-4">
              <button
                onClick={handleTakeQuiz}
                className="w-full bg-white text-black px-6 py-4 font-bold text-lg hover:bg-gray-200 transition-colors"
              >
                TAKE_QUIZ_ON_THIS_TOPIC()
              </button>

              <button
                onClick={() => {
                  setNotes(null);
                  setTopic("");
                  setGenerationTime(null);
                }}
                className="w-full border border-gray-600 px-6 py-3 hover:bg-gray-900 transition-colors"
              >
                STUDY_NEW_TOPIC()
              </button>

              <a
                href="/"
                className="block text-center text-sm text-gray-600 hover:text-white transition-colors"
              >
                ← BACK_TO_DASHBOARD
              </a>
            </div>
          </motion.div>
        )}

        {/* Initial State Help */}
        {!notes && !loading && !error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="border border-gray-700 p-6 text-center"
          >
            <p className="text-gray-500 text-sm mb-4">
              Enter any topic above to generate AI-powered study notes.
            </p>
            <div className="text-xs text-gray-600 space-y-1">
              <p>
                ✓ Topics can be any subject (science, history, programming,
                etc.)
              </p>
              <p>✓ Notes are generated using AI in ~5-10 seconds</p>
              <p>
                ✓ After studying, you can take a quiz to test your knowledge
              </p>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}

export default function StudyPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="text-2xl font-mono">LOADING...</div>
      </div>
    }>
      <StudyPageContent />
    </Suspense>
  );
}
