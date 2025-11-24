"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { useAuth } from "@/lib/useAuth";
import { supabase, LeaderboardEntry } from "@/lib/supabase";
import { useRealtimeLeaderboard } from "@/lib/useRealtimeXP";
import { createLogger } from "@/lib/logger";

const logger = createLogger("LeaderboardPage");

export default function LeaderboardPage() {
  const { userId } = useAuth();
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Subscribe to real-time updates
  const { isConnected } = useRealtimeLeaderboard();

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  // Re-fetch when real-time updates occur (only on connection, not continuously)
  useEffect(() => {
    if (isConnected) {
      // Fetch once when connected
      fetchLeaderboard();
    }
  }, [isConnected]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch real data from Supabase
      const { data, error: queryError } = await supabase
        .from("users")
        .select("id:user_id, username, total_xp, level")
        .order("total_xp", { ascending: false })
        .limit(10);

      if (queryError) {
        throw queryError;
      }

      // Add ranks to the data
      const rankedData: LeaderboardEntry[] = (data || []).map(
        (user, index) => ({
          ...user,
          rank: index + 1,
        }),
      );

      logger.info("Leaderboard data loaded", {
        entriesCount: rankedData.length,
        userId,
      });
      logger.debug("Top 3 leaderboard entries", {
        top3: rankedData
          .slice(0, 3)
          .map((e) => ({ rank: e.rank, username: e.username, xp: e.total_xp })),
      });

      // Debug first entry specifically
      if (rankedData.length > 0) {
        const first = rankedData[0];
        logger.debug("First leaderboard entry details", {
          rank: first.rank,
          id: first.id,
          username: first.username,
          total_xp: first.total_xp,
          level: first.level,
        });
      }

      setLeaderboard(rankedData);
      setLastUpdate(new Date());
    } catch (err) {
      setError("Failed to load leaderboard");
      logger.error("Leaderboard error", { userId, error: String(err) });
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number): string => {
    switch (rank) {
      case 1:
        return "👑";
      case 2:
        return "🥈";
      case 3:
        return "🥉";
      default:
        return "  ";
    }
  };

  const getRankClass = (rank: number): string => {
    switch (rank) {
      case 1:
        return "bg-terminal-white text-terminal-black";
      case 2:
        return "border-2 border-terminal-white";
      case 3:
        return "border border-terminal-white";
      default:
        return "border border-terminal-gray";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-terminal-black flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="text-terminal-white text-xl font-mono">
            LOADING LEADERBOARD<span className="animate-pulse">...</span>
          </div>
          <div className="text-terminal-gray text-sm mt-2">
            // Fetching top performers
          </div>
        </motion.div>
      </div>
    );
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
            onClick={fetchLeaderboard}
            className="w-full bg-terminal-black text-terminal-white border border-terminal-white px-6 py-3 hover:bg-terminal-white hover:text-terminal-black transition-colors"
          >
            RETRY
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-terminal-black text-terminal-white p-6 md:p-8 font-mono">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Link
            href="/"
            className="text-terminal-gray text-sm hover:text-terminal-white transition-colors mb-4 inline-block"
          >
            ← BACK_TO_DASHBOARD
          </Link>
          <div className="bg-terminal-white text-terminal-black px-6 py-4">
            <h1 className="text-3xl font-bold text-center">
              ═══════════ LEADERBOARD ═══════════
            </h1>
          </div>
        </motion.div>

        {/* Stats Summary */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="border border-terminal-gray p-4 mb-6"
        >
          <div className="flex items-center justify-between text-sm">
            <div>
              <span className="text-terminal-gray">// TOTAL_PLAYERS:</span>
              <span className="text-terminal-white ml-2">
                {leaderboard.length}
              </span>
            </div>
            <div>
              <span className="text-terminal-gray">// TOP_XP:</span>
              <span className="text-terminal-white ml-2">
                {leaderboard[0]?.total_xp || 0}
              </span>
            </div>
            <div>
              <span className="text-terminal-gray">// STATUS:</span>
              <span
                className={`ml-2 ${isConnected ? "text-terminal-white" : "text-terminal-gray"}`}
              >
                {isConnected ? "🟢 LIVE" : "🔴 OFFLINE"}
              </span>
            </div>
          </div>
        </motion.div>

        {/* ASCII Table Header */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="border border-terminal-white mb-0"
        >
          <div className="grid grid-cols-12 gap-4 p-4 bg-terminal-white text-terminal-black font-bold">
            <div className="col-span-1 text-center">RANK</div>
            <div className="col-span-5">USERNAME</div>
            <div className="col-span-3 text-right">TOTAL XP</div>
            <div className="col-span-3 text-right">LEVEL</div>
          </div>
        </motion.div>

        {/* Leaderboard Entries */}
        <div className="border-l border-r border-b border-terminal-white">
          {leaderboard.map((entry, index) => (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.005, transition: { duration: 0.1 } }}
              transition={{ delay: 0.3 + index * 0.05 }}
              className={`
                grid grid-cols-12 gap-4 p-4 bg-terminal-black
                ${entry.id === userId ? "bg-opacity-95" : ""}
                ${index < leaderboard.length - 1 ? "border-b border-terminal-gray" : ""}
              `}
              style={{ backgroundColor: "#000000" }}
            >
              {/* Rank */}
              <div className="col-span-1 text-center flex items-center justify-center">
                <span className="text-2xl">{getRankIcon(entry.rank)}</span>
                <span className="text-terminal-gray ml-2">#{entry.rank}</span>
              </div>

              {/* Username */}
              <div className="col-span-5 flex items-center">
                <span
                  className="font-mono text-terminal-white font-bold"
                  style={{ color: "#FFFFFF" }}
                >
                  {entry.username || "Unknown"}
                </span>
                {entry.id === userId && (
                  <span className="ml-2 text-xs border border-terminal-white px-2 py-1 text-terminal-white">
                    YOU
                  </span>
                )}
              </div>

              {/* Total XP */}
              <div className="col-span-3 text-right flex items-center justify-end">
                <span
                  className="font-bold text-lg font-mono"
                  style={{ color: "#FFFFFF" }}
                >
                  {entry.total_xp?.toLocaleString() || "0"}
                </span>
                <span className="text-terminal-gray ml-2 text-sm">XP</span>
              </div>

              {/* Level */}
              <div className="col-span-3 text-right flex items-center justify-end">
                <div
                  className={`
                  px-3 py-1 border
                  ${entry.rank === 1 ? "border-terminal-white bg-terminal-white text-terminal-black" : "border-terminal-gray text-terminal-white"}
                `}
                >
                  LVL {entry.level}
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-8 text-center text-terminal-gray text-sm space-y-2"
        >
          <p>Last updated: {lastUpdate.toLocaleTimeString()}</p>
          <p>Rankings update in real-time as players earn XP</p>
          <p className="text-xs mt-4">
            $ leaderboard --top=10 --live={isConnected ? "true" : "false"}
          </p>
        </motion.div>
      </div>
    </div>
  );
}
