"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/useAuth";
import CoachFeedbackPanel from "@/components/CoachFeedbackPanel";
import { useLoadingState } from "@/hooks/useLoadingState";
import { generateXPBar, calculateXPToNextLevel } from "@/utils/xp";
import { getStatusSymbol } from "@/utils/formatting";
import { getApi } from "@/utils/api";
import { createLogger } from "@/lib/logger";

const logger = createLogger("ProgressPage");

interface TopicProgress {
  topic: string;
  status: string;
  score: number;
  best_score: number;
  attempts: number;
  last_attempted_at: string;
}

interface UserStats {
  total_topics: number;
  mastered_count: number;
  completed_count: number;
  in_progress_count: number;
  avg_best_score: number;
  total_attempts: number;
}

interface UserData {
  total_xp: number;
  level: number;
  username: string;
}

export default function ProgressDashboard() {
  const { userId, loading: authLoading } = useAuth();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [topics, setTopics] = useState<TopicProgress[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const { isLoading, setLoading } = useLoadingState(true);
  const [retryingTopic, setRetryingTopic] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !userId) {
      router.push("/login");
    }
  }, [authLoading, userId, router]);

  useEffect(() => {
    if (userId) {
      fetchProgressData();
    }
  }, [userId]);

  const fetchProgressData = async () => {
    if (!userId) return;

    try {
      setLoading(true);

      const API_BASE =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      // Fetch user stats from v2 API
      const statsRes = await fetch(
        `${API_BASE}/progress/v2/user/${userId}/stats`,
      );
      const statsData = await statsRes.json();

      // Fetch topics from v2 API
      const topicsRes = await fetch(
        `${API_BASE}/progress/v2/user/${userId}/topics`,
      );
      const topicsData = await topicsRes.json();

      // Map v2 data to existing interface
      const userData: UserData = {
        total_xp: statsData.total_xp || 0,
        level: statsData.level || 1,
        username: userId,
      };

      const topics: TopicProgress[] = (topicsData.topics || []).map(
        (t: any) => ({
          topic: t.topic,
          status: t.status,
          score: t.best_score, // v2 doesn't have separate score, use best
          best_score: t.best_score,
          attempts: t.attempts,
          last_attempted_at: t.last_attempted,
        }),
      );

      const stats: UserStats = {
        total_topics: statsData.topics_started || 0,
        mastered_count: statsData.topics_mastered || 0,
        completed_count: statsData.topics_completed || 0,
        in_progress_count:
          statsData.topics_started -
          statsData.topics_completed -
          statsData.topics_mastered,
        avg_best_score: statsData.average_score || 0,
        total_attempts: statsData.quizzes_completed || 0,
      };

      setUserData(userData);
      setTopics(topics);
      setStats(stats);
    } catch (error) {
      logger.error("Error fetching progress", { userId, error: String(error) });
    } finally {
      setLoading(false);
    }
  };

  const handleRetryTopic = async (topic: string) => {
    try {
      setRetryingTopic(topic);

      // Call retry endpoint via API proxy
      const response = await fetch("/api/study/retry", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: topic,
          num_questions: 5,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to retry topic");
      }

      const data = await response.json();

      // Store study package in sessionStorage
      sessionStorage.setItem("currentStudyPackage", JSON.stringify(data));
      sessionStorage.setItem("currentTopic", topic);
      sessionStorage.setItem("isRetry", "true");

      // Navigate to study page
      router.push("/");
    } catch (error) {
      logger.error("Error retrying topic", {
        userId,
        topic,
        error: String(error),
      });
      alert("Failed to retry topic. Please try again.");
    } finally {
      setRetryingTopic(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center font-mono">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="text-xl">
            LOADING PROGRESS DATA<span className="animate-pulse">...</span>
          </div>
          <div className="text-gray-500 mt-2">// Fetching your stats</div>
        </motion.div>
      </div>
    );
  }

  const xpToNextLevel = userData
    ? calculateXPToNextLevel(userData.total_xp)
    : 500;

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
              ═══════════ PROGRESS DASHBOARD ═══════════
            </h1>
          </div>
        </motion.div>

        {/* User Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="border border-gray-700 p-6 mb-6"
        >
          <div className="text-sm text-gray-500 mb-2">
            // USER: {userData?.username || "demo_user"}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* XP Section */}
            <div>
              <div className="text-2xl mb-2">LEVEL {userData?.level || 1}</div>
              <div className="text-gray-500 mb-3">
                {userData?.total_xp || 0} XP TOTAL
              </div>
              <div className="mb-2 font-bold text-sm">
                {generateXPBar(userData?.total_xp || 0)}
              </div>
              <div className="text-xs text-gray-500">
                {xpToNextLevel} XP TO NEXT LEVEL
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 gap-4 text-center">
              <div className="border border-gray-700 p-3">
                <div className="text-3xl font-bold">
                  {stats?.total_topics || 0}
                </div>
                <div className="text-xs text-gray-500 mt-1">TOPICS</div>
              </div>
              <div className="border border-gray-700 p-3">
                <div className="text-3xl font-bold">
                  {stats?.total_attempts || 0}
                </div>
                <div className="text-xs text-gray-500 mt-1">ATTEMPTS</div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        >
          <div className="border border-gray-700 p-4">
            <div className="text-gray-500 text-xs mb-2">// MASTERED</div>
            <div className="text-2xl font-bold">
              {stats?.mastered_count || 0}
            </div>
            <div className="text-xs text-gray-500 mt-1">★★★</div>
          </div>
          <div className="border border-gray-700 p-4">
            <div className="text-gray-500 text-xs mb-2">// COMPLETED</div>
            <div className="text-2xl font-bold">
              {stats?.completed_count || 0}
            </div>
            <div className="text-xs text-gray-500 mt-1">★★☆</div>
          </div>
          <div className="border border-gray-700 p-4">
            <div className="text-gray-500 text-xs mb-2">// IN PROGRESS</div>
            <div className="text-2xl font-bold">
              {stats?.in_progress_count || 0}
            </div>
            <div className="text-xs text-gray-500 mt-1">★☆☆</div>
          </div>
          <div className="border border-gray-700 p-4">
            <div className="text-gray-500 text-xs mb-2">// AVG ACCURACY</div>
            <div className="text-2xl font-bold">
              {(stats?.avg_best_score ?? 0).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">BEST SCORES</div>
          </div>
        </motion.div>

        {/* Adaptive Coach Feedback */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <CoachFeedbackPanel userId={userId || ""} />
        </motion.div>

        {/* Topics Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="border border-white mb-0">
            <div className="bg-white text-black px-6 py-3">
              <h2 className="text-xl font-bold">TOPIC BREAKDOWN</h2>
            </div>
          </div>

          {/* Table Header */}
          <div className="border-l border-r border-b border-white">
            <div className="grid grid-cols-12 gap-4 p-4 bg-gray-900 text-xs font-bold border-b border-gray-700">
              <div className="col-span-1">RANK</div>
              <div className="col-span-3">TOPIC</div>
              <div className="col-span-2 text-center">STATUS</div>
              <div className="col-span-1 text-right">SCORE</div>
              <div className="col-span-2 text-right">BEST</div>
              <div className="col-span-1 text-right">ATTEMPTS</div>
              <div className="col-span-2 text-center">ACTION</div>
            </div>

            {/* Table Rows */}
            {topics.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <div className="text-lg mb-2">NO TOPICS YET</div>
                <div className="text-sm">
                  // Start learning to see your progress here
                </div>
              </div>
            ) : (
              topics.map((topic, index) => (
                <motion.div
                  key={topic.topic}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 + index * 0.05 }}
                  whileHover={{ scale: 1.005, transition: { duration: 0.1 } }}
                  className={`
                    grid grid-cols-12 gap-4 p-4 
                    ${index < topics.length - 1 ? "border-b border-gray-800" : ""}
                  `}
                >
                  {/* Rank */}
                  <div className="col-span-1 text-gray-500">
                    #{(index + 1).toString().padStart(2, "0")}
                  </div>

                  {/* Topic Name */}
                  <div className="col-span-3 font-bold">{topic.topic}</div>

                  {/* Status */}
                  <div className="col-span-2 text-center">
                    <span
                      className={`
                      px-2 py-1 text-xs
                      ${topic.status === "mastered" ? "bg-white text-black" : ""}
                      ${topic.status === "completed" ? "border border-white" : ""}
                      ${topic.status === "in_progress" ? "border border-gray-700 text-gray-500" : ""}
                    `}
                    >
                      {getStatusSymbol(topic.status)}{" "}
                      {topic.status.toUpperCase()}
                    </span>
                  </div>

                  {/* Latest Score */}
                  <div className="col-span-1 text-right text-gray-400">
                    {(topic.score ?? 0).toFixed(1)}%
                  </div>

                  {/* Best Score */}
                  <div className="col-span-2 text-right font-bold">
                    {(topic.best_score ?? 0).toFixed(1)}%
                  </div>

                  {/* Attempts */}
                  <div className="col-span-1 text-right text-gray-500">
                    {topic.attempts}x
                  </div>

                  {/* Retry Action */}
                  <div className="col-span-2 text-center">
                    {(topic.status === "completed" ||
                      topic.status === "mastered" ||
                      topic.status === "in_progress") && (
                      <motion.button
                        onClick={() => handleRetryTopic(topic.topic)}
                        disabled={retryingTopic === topic.topic}
                        whileHover={{
                          scale: retryingTopic === topic.topic ? 1 : 1.02,
                        }}
                        whileTap={{
                          scale: retryingTopic === topic.topic ? 1 : 0.98,
                        }}
                        className={`
                          px-3 py-1 text-xs font-mono border transition-colors
                          ${
                            retryingTopic === topic.topic
                              ? "border-gray-700 text-gray-700 cursor-not-allowed"
                              : "border-white text-white hover:bg-white hover:text-black"
                          }
                        `}
                      >
                        {retryingTopic === topic.topic
                          ? "[LOADING...]"
                          : "[↻ RETRY]"}
                      </motion.button>
                    )}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 text-center text-gray-500 text-sm space-y-2"
        >
          <p>Progress updates in real-time</p>
          <p className="text-xs">
            $ progress --user=demo_user --format=terminal
          </p>
        </motion.div>
      </div>
    </div>
  );
}
