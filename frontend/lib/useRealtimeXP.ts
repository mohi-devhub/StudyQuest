import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';

interface UseRealtimeXPProps {
  userId: string;
  onXPGain?: (points: number, reason: string, topic?: string) => void;
  onLevelUp?: (newLevel: number) => void;
  onProgressUpdate?: (topic: string, avgScore: number) => void;
}

interface UseRealtimeLeaderboardProps {
  userId?: string;
}

export const useRealtimeXP = ({ userId, onXPGain, onLevelUp, onProgressUpdate }: UseRealtimeXPProps) => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!userId) return;

    const xpChannel = supabase
      .channel('public:xp_logs')
      .on(
        'postgres_changes',
        { event: 'INSERT', schema: 'public', table: 'xp_logs', filter: `user_id=eq.${userId}` },
        (payload) => {
          console.log('XP change received!', payload);
          if (onXPGain) {
            onXPGain(payload.new.points, payload.new.reason, payload.new.metadata?.topic);
          }
        }
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      });

    const progressChannel = supabase
      .channel('public:progress')
      .on(
        'postgres_changes',
        { event: 'UPDATE', schema: 'public', table: 'progress', filter: `user_id=eq.${userId}` },
        (payload) => {
          console.log('Progress change received!', payload);
          if (onProgressUpdate) {
            onProgressUpdate(payload.new.topic, payload.new.avg_score);
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(xpChannel);
      supabase.removeChannel(progressChannel);
    };
  }, [userId, onXPGain, onLevelUp, onProgressUpdate]);

  return { isConnected };
};

export const useRealtimeLeaderboard = ({ userId }: UseRealtimeLeaderboardProps = {}) => {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const channel = supabase
      .channel('public:users')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'users' },
        (payload) => {
          console.log('Leaderboard change received!', payload);
          fetchLeaderboard();
        }
      )
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      });

    const fetchLeaderboard = async () => {
      const { data, error } = await supabase
        .from('users')
        .select('id:user_id, username, total_xp, level')
        .order('total_xp', { ascending: false })
        .limit(10);

      if (error) {
        console.error('Error fetching leaderboard:', error);
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
