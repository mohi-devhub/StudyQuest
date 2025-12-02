import { useEffect, useState } from "react";

interface Badge {
  badge_key: string;
  name: string;
  description: string;
  symbol: string;
  tier: number;
  unlocked_at: string;
}

interface UseRealtimeXPOptions {
  userId: string;
  onXPGain?: (xp: number, source: string, topic?: string) => void;
  onLevelUp?: (newLevel: number) => void;
  onProgressUpdate?: (topic: string, newAvgScore: number) => void;
  onBadgeUnlock?: (badge: Badge) => void;
}

export function useRealtimeXP({
  userId,
  onXPGain: _onXPGain,
  onLevelUp: _onLevelUp,
  onProgressUpdate: _onProgressUpdate,
  onBadgeUnlock: _onBadgeUnlock,
}: UseRealtimeXPOptions) {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!userId) return;

    // For now, just set connected to true
    // In the future, this could connect to a WebSocket or Supabase Realtime
    setIsConnected(true);

    return () => {
      setIsConnected(false);
    };
  }, [userId]);

  return { isConnected };
}

export function useRealtimeLeaderboard() {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    // For now, just set connected to true
    // In the future, this could connect to a WebSocket or Supabase Realtime for live leaderboard updates
    setIsConnected(true);
  }, []);

  return { isConnected };
}
