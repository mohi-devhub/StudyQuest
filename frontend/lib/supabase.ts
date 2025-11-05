import { createBrowserClient } from '@supabase/ssr'

export const supabase = createBrowserClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export type LeaderboardEntry = {
  id: string;
  username: string;
  total_xp: number;
  rank: number;
  level: number;
};