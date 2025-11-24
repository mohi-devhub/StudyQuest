import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";

interface UseRealtimeXPProps {
  userId: string;
  onXPGain?: (points: number, reason: string, topic?: string) => void;
  onLevelUp?: (newLevel: number) => void;
  onProgressUpdate?: (topic: string, avgScore: number) => void;
  onBadgeUnlock?: (badge: UnlockedBadge) => void;
}

interface UseRealtimeLeaderboardProps {
  userId?: string;
}

interface UnlockedBadge {
  badge_key: string;
  name: string;
  description: string;
  symbol: string;
  tier: number;
  unlocked_at: string;
}

export const useRealtimeXP = ({
  userId,
  onXPGain,
  onLevelUp,
  onProgressUpdate,
  onBadgeUnlock,
}: UseRealtimeXPProps) => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!userId) return;

    const xpChannel = supabase
      .channel("public:xp_logs")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "xp_logs",
          filter: `user_id=eq.${userId}`,
        },
        (payload) => {
          console.log("XP change received!", payload);
          if (onXPGain) {
            onXPGain(
              payload.new.points,
              payload.new.reason,
              payload.new.metadata?.topic,
            );
          }
        },
      )
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      });

    const progressChannel = supabase
      .channel("public:progress")
      .on(
        "postgres_changes",
        {
          event: "UPDATE",
          schema: "public",
          table: "progress",
          filter: `user_id=eq.${userId}`,
        },
        (payload) => {
          console.log("Progress change received!", payload);
          if (onProgressUpdate) {
            onProgressUpdate(payload.new.topic, payload.new.avg_score);
          }
        },
      )
      .subscribe();

    // Listen for new badge unlocks
    const badgeChannel = supabase
      .channel("public:user_badges")
      .on(
        "postgres_changes",
        {
          event: "INSERT",
          schema: "public",
          table: "user_badges",
          filter: `user_id=eq.${userId}`,
        },
        async (payload) => {
          console.log("Badge unlock received!", payload);

          // Fetch full badge details
          if (onBadgeUnlock) {
            try {
              const { data, error } = await supabase
                .from("user_badges")
                .select(
                  `
                  unlocked_at,
                  badges (
                    badge_key,
                    name,
                    description,
                    symbol,
                    tier
                  )
                `,
                )
                .eq("id", payload.new.id)
                .single();

              if (data && !error && data.badges) {
                const badge = Array.isArray(data.badges)
                  ? data.badges[0]
                  : data.badges;
                onBadgeUnlock({
                  badge_key: badge.badge_key,
                  name: badge.name,
                  description: badge.description,
                  symbol: badge.symbol,
                  tier: badge.tier,
                  unlocked_at: data.unlocked_at,
                });
              }
            } catch (err) {
              console.error("Error fetching badge details:", err);
            }
          }
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(xpChannel);
      supabase.removeChannel(progressChannel);
      supabase.removeChannel(badgeChannel);
    };
  }, [userId, onXPGain, onLevelUp, onProgressUpdate, onBadgeUnlock]);

  return { isConnected };
};

export const useRealtimeLeaderboard = ({
  userId,
}: UseRealtimeLeaderboardProps = {}) => {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const channel = supabase
      .channel("public:users")
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "users" },
        (payload) => {
          console.log("Leaderboard change received!", payload);
          fetchLeaderboard();
        },
      )
      .subscribe((status) => {
        if (status === "SUBSCRIBED") {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      });

    const fetchLeaderboard = async () => {
      const { data, error } = await supabase
        .from("users")
        .select("id:user_id, username, total_xp, level")
        .order("total_xp", { ascending: false })
        .limit(10);

      if (error) {
        console.error("Error fetching leaderboard:", error);
        return;
      }

      const rankedData = (data || []).map((user, index) => ({
        ...user,
        rank: index + 1,
      }));

      setLeaderboard(rankedData);
    };

    fetchLeaderboard();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [userId]);

  return { leaderboard, isConnected };
};
