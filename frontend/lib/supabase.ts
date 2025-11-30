import { createBrowserClient } from "@supabase/ssr";

// Provide fallback values for build time
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key';

export const supabase = createBrowserClient(
  supabaseUrl,
  supabaseAnonKey,
);

export type LeaderboardEntry = {
  id: string;
  username: string;
  total_xp: number;
  rank: number;
  level: number;
};
