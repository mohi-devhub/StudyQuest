-- ===========================================================================
-- VERIFY AND FIX REALTIME CONFIGURATION
-- ===========================================================================
-- Run this in Supabase SQL Editor to check and enable realtime
-- ===========================================================================

-- 1. Check if tables are in realtime publication
SELECT schemaname, tablename 
FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime';

-- Expected output: Should show users, progress, xp_logs, quiz_results
-- If empty or missing tables, run the following:

-- 2. Enable realtime (may fail if already added, that's OK)
ALTER PUBLICATION supabase_realtime ADD TABLE public.users;
ALTER PUBLICATION supabase_realtime ADD TABLE public.progress;
ALTER PUBLICATION supabase_realtime ADD TABLE public.xp_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_results;

-- 3. Verify tables exist
SELECT tablename, schemaname 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('users', 'progress', 'xp_logs', 'quiz_results');

-- 4. Check RLS is enabled (should all be true)
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public'
AND tablename IN ('users', 'progress', 'xp_logs', 'quiz_results');

-- 5. Verify RLS policies allow SELECT (needed for realtime)
SELECT schemaname, tablename, policyname, cmd
FROM pg_policies 
WHERE schemaname = 'public'
AND tablename IN ('users', 'progress', 'xp_logs', 'quiz_results')
AND cmd = 'SELECT';

-- ===========================================================================
-- TROUBLESHOOTING
-- ===========================================================================

-- If realtime still doesn't work, try:

-- Option 1: Drop and re-add tables to publication
ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS public.users;
ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS public.progress;
ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS public.xp_logs;
ALTER PUBLICATION supabase_realtime DROP TABLE IF EXISTS public.quiz_results;

ALTER PUBLICATION supabase_realtime ADD TABLE public.users;
ALTER PUBLICATION supabase_realtime ADD TABLE public.progress;
ALTER PUBLICATION supabase_realtime ADD TABLE public.xp_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_results;

-- Option 2: Check if realtime is enabled in project settings
-- Go to: Database > Replication > Enable Realtime for tables

-- Option 3: Verify database has realtime extension
SELECT * FROM pg_extension WHERE extname = 'pg_stat_statements';

-- ===========================================================================
-- FINAL VERIFICATION
-- ===========================================================================

-- Run this to confirm everything is set up:
SELECT 
  t.tablename,
  t.rowsecurity as rls_enabled,
  CASE WHEN p.tablename IS NOT NULL THEN true ELSE false END as realtime_enabled
FROM pg_tables t
LEFT JOIN pg_publication_tables p 
  ON p.schemaname = t.schemaname 
  AND p.tablename = t.tablename 
  AND p.pubname = 'supabase_realtime'
WHERE t.schemaname = 'public'
AND t.tablename IN ('users', 'progress', 'xp_logs', 'quiz_results')
ORDER BY t.tablename;

-- All rows should show: rls_enabled = true, realtime_enabled = true
