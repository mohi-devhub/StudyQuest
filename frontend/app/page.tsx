"use client";

import { useEffect, useState, useCallback } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Header from "@/components/Header";
import XPProgressBar from "@/components/XPProgressBar";
import TopicCard from "@/components/TopicCard";
import RecommendedCard from "@/components/RecommendedCard";
import LoadingScreen from "@/components/LoadingScreen";
import { useToast } from "@/components/Toast";
import { useRealtimeXP } from "@/lib/useRealtimeXP";
import { useAuth } from "@/lib/useAuth";
import { useLoadingState } from "@/hooks/useLoadingState";
import { useErrorState } from "@/hooks/useErrorState";
import { fetchDashboardData, fetchRecommendations } from "@/utils/api";
import CelebrationModal from "@/components/CelebrationModal";
import { createLogger } from "@/lib/logger";

const logger = createLogger("HomePage");

interface UserProgress {
  user_id: string;
  total_xp: number;
  level: number;
  topics: Array<{
    topic: string;
    avg_score: number;
    total_attempts: number;
    last_attempt: string;
  }>;
}

interface Recommendation {
  topic: string;
  reason: string;
  priority: string;
  category: string;
  current_score: number | null;
  recommended_difficulty: string;
  estimated_xp_gain: number;
  urgency: string;
}

interface RecommendationResponse {
  recommendations: Recommendation[];
  overall_stats?: {
    total_attempts: number;
    avg_score: number;
    topics_studied: number;
  };
  ai_insights?: {
    motivational_message: string;
    learning_insight: string;
    priority_advice: string;
  };
}

export default function Dashboard() {
  const { userId, user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [recommendations, setRecommendations] =
    useState<RecommendationResponse | null>(null);
  const { isLoading, withLoading } = useLoadingState(true);
  const { error, withErrorHandling, setError } = useErrorState(null);
  const [showXPSummary, setShowXPSummary] = useState(false);
  const [xpSummaryData, setXPSummaryData] = useState<any>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !userId) {
      router.push("/login");
    }
  }, [authLoading, userId, router]);

  // Celebration states
  const [celebration, setCelebration] = useState<{
    isOpen: boolean;
    type: "level" | "badge";
    title: string;
    message: string;
    symbol?: string;
  }>({
    isOpen: false,
    type: "level",
    title: "",
    message: "",
  });

  // Real-time updates
  const { showToast, ToastContainer } = useToast();

  // Stable callbacks for real-time events
  const handleXPGain = useCallback(
    (xp: number, source: string, topic?: string) => {
      logger.info("XP gained", {
        xp,
        source,
        topic: topic || "unknown",
        userId,
      });
      showToast(`${topic || "Study"} completed!`, xp, "xp");

      // Update progress with new XP
      setProgress((prev) => {
        if (!prev) return prev;
        const newTotalXP = prev.total_xp + xp;
        const newLevel = Math.floor(newTotalXP / 500) + 1;

        // Check for level up
        if (newLevel > prev.level) {
          handleLevelUp(newLevel);
        }

        return {
          ...prev,
          total_xp: newTotalXP,
          level: newLevel,
        };
      });
    },
    [showToast],
  );

  const handleLevelUp = useCallback(
    (newLevel: number) => {
      logger.info("Level up achieved", { newLevel, userId });
      showToast(`LEVEL UP! Now level ${newLevel}`, undefined, "success");

      // Show celebration modal
      const levelTitles: { [key: number]: string } = {
        5: "Novice Scholar",
        10: "Curious Mind",
        15: "Dedicated Learner",
        20: "Knowledge Seeker",
        25: "Wise Student",
        30: "Sage",
      };

      const title = levelTitles[newLevel] || "Knowledge Seeker";

      setCelebration({
        isOpen: true,
        type: "level",
        title: `🎉 LEVEL UP!`,
        message: `You are now Level ${newLevel} – ${title}`,
      });
    },
    [showToast],
  );

  const handleBadgeUnlock = useCallback(
    (badge: any) => {
      logger.info("Badge unlocked", {
        badgeName: badge.name,
        badgeKey: badge.badge_key,
        userId,
      });
      showToast(`Badge Unlocked: ${badge.name}`, undefined, "success");

      // Show celebration modal
      setCelebration({
        isOpen: true,
        type: "badge",
        title: `🏆 BADGE UNLOCKED!`,
        message: badge.description,
        symbol: badge.symbol,
      });
    },
    [showToast],
  );

  const handleProgressUpdate = useCallback(
    (topic: string, newAvgScore: number) => {
      logger.debug("Progress updated", { topic, newAvgScore, userId });

      // Update topic in progress
      setProgress((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          topics: prev.topics.map((t) =>
            t.topic === topic ? { ...t, avg_score: newAvgScore } : t,
          ),
        };
      });
    },
    [],
  );

  // Subscribe to real-time XP updates
  const { isConnected } = useRealtimeXP({
    userId: userId || "",
    onXPGain: handleXPGain,
    onLevelUp: handleLevelUp,
    onProgressUpdate: handleProgressUpdate,
    onBadgeUnlock: handleBadgeUnlock,
  });

  const loadDashboard = useCallback(async () => {
    if (!userId) return;

    await withLoading(async () => {
      const data = await withErrorHandling(async () =>
        fetchDashboardData(userId),
      );

      if (data && data.progress) {
        setProgress({
          user_id: userId,
          total_xp: data.progress.user?.total_xp || 0,
          level: data.progress.user?.level || 1,
          topics: data.progress.topics || [],
        });

        // Set empty recommendations initially
        setRecommendations({
          recommendations: [],
          overall_stats: {
            total_attempts: 0,
            avg_score: 0,
            topics_studied: 0,
          },
        });
      } else {
        // Set empty state on failure
        setProgress({
          user_id: userId,
          total_xp: 0,
          level: 1,
          topics: [],
        });
        setRecommendations({
          recommendations: [],
          overall_stats: {
            total_attempts: 0,
            avg_score: 0,
            topics_studied: 0,
          },
        });
      }
    });
  }, [userId, withLoading, withErrorHandling]);

  const loadRecommendations = useCallback(async () => {
    if (!userId) return;

    try {
      const recs = await fetchRecommendations(userId);
      setRecommendations(recs);
    } catch (error) {
      console.error("Failed to load recommendations:", error);
      // Keep empty recommendations on error
    }
  }, [userId]);

  useEffect(() => {
    if (userId) {
      loadDashboard();

      // Load recommendations separately (in background)
      loadRecommendations();

      // Check if this is a retry session
      const isRetry = sessionStorage.getItem("isRetry");
      const studyPackage = sessionStorage.getItem("currentStudyPackage");

      if (isRetry === "true" && studyPackage) {
        const data = JSON.parse(studyPackage);
        if (data.metadata?.retry && data.metadata?.xp_earned) {
          setXPSummaryData({
            topic: data.topic,
            xp_earned: data.metadata.xp_earned,
            total_xp: data.metadata.total_xp,
            level: data.metadata.level,
          });
          setShowXPSummary(true);

          // Clear retry flag after showing summary
          sessionStorage.removeItem("isRetry");
        }
      }
    }
  }, [userId, loadDashboard, loadRecommendations]);

  if (authLoading || isLoading) {
    return <LoadingScreen />;
  }

  if (!userId) {
    return null; // Will redirect via useEffect
  }

  if (error) {
    return (
      <div className="min-h-screen bg-terminal-black flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border border-terminal-white p-8 max-w-md w-full"
        >
          <h2 className="text-2xl mb-4">// ERROR</h2>
          <p className="text-terminal-gray mb-6">{error}</p>
          <button
            onClick={loadDashboard}
            className="w-full bg-terminal-black text-terminal-white border border-terminal-white px-6 py-3 hover:bg-terminal-white hover:text-terminal-black transition-colors"
          >
            RETRY
          </button>
        </motion.div>
      </div>
    );
  }

  if (!progress || !recommendations) {
    return null;
  }

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <Header />

        {/* XP Progress Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mt-8"
        >
          <XPProgressBar currentXP={progress.total_xp} level={progress.level} />
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4"
        >
          <Link
            href="/study"
            className="border border-terminal-white p-6 hover:bg-terminal-white hover:text-terminal-black transition-colors text-center group"
          >
            <div className="text-sm text-terminal-gray group-hover:text-terminal-black mb-2">
              // ACTION_01
            </div>
            <div className="text-xl font-bold">START_NEW_STUDY_SESSION()</div>
            <div className="text-sm text-terminal-gray group-hover:text-terminal-black mt-2">
              Generate AI study notes on any topic
            </div>
          </Link>

          <Link
            href="/quiz"
            className="border border-terminal-white p-6 hover:bg-terminal-white hover:text-terminal-black transition-colors text-center group"
          >
            <div className="text-sm text-terminal-gray group-hover:text-terminal-black mb-2">
              // ACTION_02
            </div>
            <div className="text-xl font-bold">TAKE_QUIZ()</div>
            <div className="text-sm text-terminal-gray group-hover:text-terminal-black mt-2">
              Test your knowledge with AI-generated quizzes
            </div>
          </Link>
        </motion.div>

        {/* Stats Overview */}
        {recommendations.overall_stats && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div className="border border-terminal-white p-4">
              <div className="text-terminal-gray text-sm mb-1">
                // TOTAL_QUIZZES
              </div>
              <div className="text-3xl font-bold">
                {recommendations.overall_stats.total_attempts}
              </div>
            </div>
            <div className="border border-terminal-white p-4">
              <div className="text-terminal-gray text-sm mb-1">
                // AVG_SCORE
              </div>
              <div className="text-3xl font-bold">
                {recommendations.overall_stats.avg_score.toFixed(1)}%
              </div>
            </div>
            <div className="border border-terminal-white p-4">
              <div className="text-terminal-gray text-sm mb-1">
                // TOPICS_STUDIED
              </div>
              <div className="text-3xl font-bold">
                {recommendations.overall_stats.topics_studied}
              </div>
            </div>
          </motion.div>
        )}

        {/* AI Insights */}
        {recommendations.ai_insights && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-8 border border-terminal-gray p-6"
          >
            <div className="text-sm text-terminal-gray mb-2">
              // AI_INSIGHTS
            </div>
            <p className="text-terminal-white mb-4">
              {recommendations.ai_insights.motivational_message}
            </p>
            <p className="text-terminal-gray text-sm">
              {recommendations.ai_insights.priority_advice}
            </p>
          </motion.div>
        )}

        {/* Recommended Topic (Top Priority) */}
        {recommendations.recommendations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mt-8"
          >
            <h2 className="text-xl mb-4">// NEXT_RECOMMENDED</h2>
            <RecommendedCard
              recommendation={recommendations.recommendations[0]}
            />
          </motion.div>
        )}

        {/* Recent Topics */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12"
        >
          <h2 className="text-xl mb-4">// YOUR_TOPICS</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {progress.topics.map((topic, index) => (
              <TopicCard
                key={topic.topic}
                topic={topic}
                delay={0.6 + index * 0.1}
              />
            ))}
          </div>
        </motion.div>

        {/* Other Recommendations */}
        {recommendations.recommendations.length > 1 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="mt-12"
          >
            <h2 className="text-xl mb-4">// OTHER_RECOMMENDATIONS</h2>
            <div className="space-y-3">
              {recommendations.recommendations.slice(1, 4).map((rec, index) => (
                <motion.div
                  key={rec.topic}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.9 + index * 0.1 }}
                  className="border border-terminal-gray p-4 hover:border-terminal-white transition-colors cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <div className="text-sm text-terminal-gray mb-1">
                        [{rec.priority.toUpperCase()}] {rec.category}
                      </div>
                      <div className="text-lg font-medium">{rec.topic}</div>
                    </div>
                    <div className="text-terminal-gray text-sm">
                      +{rec.estimated_xp_gain} XP
                    </div>
                  </div>
                  <div className="text-sm text-terminal-gray">{rec.reason}</div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.2 }}
          className="mt-16 pt-8 border-t border-terminal-gray text-center text-terminal-gray text-sm"
        >
          <p>StudyQuest v1.0 // Monochrome Terminal Dashboard</p>
          <p className="mt-2">
            Real-time updates:{" "}
            {isConnected ? "🟢 CONNECTED" : "🔴 DISCONNECTED"}
          </p>
        </motion.div>
      </div>

      {/* Toast Notifications */}
      <ToastContainer />

      {/* Celebration Modal */}
      <CelebrationModal
        type={celebration.type}
        title={celebration.title}
        message={celebration.message}
        symbol={celebration.symbol}
        isOpen={celebration.isOpen}
        onClose={() => setCelebration((prev) => ({ ...prev, isOpen: false }))}
      />

      {/* XP Summary Modal (for retry completion) */}
      {showXPSummary && xpSummaryData && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4"
          onClick={() => setShowXPSummary(false)}
        >
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="border border-white bg-black p-8 max-w-md w-full font-mono"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-2">
                // RETRY COMPLETE
              </div>
              <h2 className="text-2xl font-bold mb-6 border-b border-white pb-4">
                XP SUMMARY
              </h2>

              <div className="space-y-4 text-left mb-6">
                <div className="border border-gray-700 p-4">
                  <div className="text-xs text-gray-500 mb-1">TOPIC</div>
                  <div className="text-lg font-bold">{xpSummaryData.topic}</div>
                </div>

                <div className="border border-gray-700 p-4 bg-white text-black">
                  <div className="text-xs text-gray-700 mb-1">XP EARNED</div>
                  <div className="text-3xl font-bold">
                    +{xpSummaryData.xp_earned} XP
                  </div>
                  <div className="text-xs text-gray-700 mt-1">for retry</div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="border border-gray-700 p-3">
                    <div className="text-xs text-gray-500 mb-1">TOTAL XP</div>
                    <div className="text-xl font-bold">
                      {xpSummaryData.total_xp}
                    </div>
                  </div>
                  <div className="border border-gray-700 p-3">
                    <div className="text-xs text-gray-500 mb-1">LEVEL</div>
                    <div className="text-xl font-bold">
                      {xpSummaryData.level}
                    </div>
                  </div>
                </div>
              </div>

              <div className="text-xs text-gray-500 mb-4 p-3 border border-gray-700">
                <code className="block">
                  $ echo "+{xpSummaryData.xp_earned} XP earned for retry on{" "}
                  {xpSummaryData.topic}"<br />
                  Total XP: {xpSummaryData.total_xp} | Level{" "}
                  {xpSummaryData.level}
                </code>
              </div>

              <button
                onClick={() => setShowXPSummary(false)}
                className="w-full border border-white px-6 py-3 hover:bg-white hover:text-black transition-colors font-mono"
              >
                [CONTINUE]
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
