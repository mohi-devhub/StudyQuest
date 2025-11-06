-- ===========================================================================
-- UPDATE RLS POLICIES FOR PRODUCTION (NO DEMO_USER)
-- ===========================================================================
-- This migration updates RLS policies to ONLY allow authenticated users.
-- 
-- ⚠️ WARNING: This removes demo_user access completely!
-- Only use this in production with real authentication enabled.
-- ===========================================================================

-- ===========================================================================
-- STEP 1: DROP ALL EXISTING POLICIES
-- ===========================================================================

-- Users table
DROP POLICY IF EXISTS "Public profiles are viewable by everyone" ON public.users;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;

-- Progress table
DROP POLICY IF EXISTS "Users can view own progress" ON public.progress;
DROP POLICY IF EXISTS "Users can view all progress" ON public.progress;
DROP POLICY IF EXISTS "Users can insert own progress" ON public.progress;
DROP POLICY IF EXISTS "Users can insert progress" ON public.progress;
DROP POLICY IF EXISTS "Users can update own progress" ON public.progress;
DROP POLICY IF EXISTS "Users can update progress" ON public.progress;

-- XP logs table
DROP POLICY IF EXISTS "Users can view own xp_logs" ON public.xp_logs;
DROP POLICY IF EXISTS "Users can view all xp logs" ON public.xp_logs;
DROP POLICY IF EXISTS "Users can insert own xp_logs" ON public.xp_logs;
DROP POLICY IF EXISTS "Users can insert xp logs" ON public.xp_logs;

-- Quiz results table
DROP POLICY IF EXISTS "Users can view own quiz_results" ON public.quiz_results;
DROP POLICY IF EXISTS "Users can view all quiz results" ON public.quiz_results;
DROP POLICY IF EXISTS "Users can insert own quiz_results" ON public.quiz_results;
DROP POLICY IF EXISTS "Users can insert quiz results" ON public.quiz_results;

-- Quiz scores table
DROP POLICY IF EXISTS "Users can view own quiz_scores" ON public.quiz_scores;
DROP POLICY IF EXISTS "Users can view all quiz scores" ON public.quiz_scores;
DROP POLICY IF EXISTS "Users can insert own quiz_scores" ON public.quiz_scores;
DROP POLICY IF EXISTS "Users can insert quiz scores" ON public.quiz_scores;

-- User topics table
DROP POLICY IF EXISTS "Users can view own user_topics" ON public.user_topics;
DROP POLICY IF EXISTS "Users can view all topics" ON public.user_topics;
DROP POLICY IF EXISTS "Users can insert own user_topics" ON public.user_topics;
DROP POLICY IF EXISTS "Users can insert topics" ON public.user_topics;
DROP POLICY IF EXISTS "Users can update own user_topics" ON public.user_topics;
DROP POLICY IF EXISTS "Users can update topics" ON public.user_topics;

-- XP history table
DROP POLICY IF EXISTS "Users can view own xp_history" ON public.xp_history;
DROP POLICY IF EXISTS "Users can view all xp history" ON public.xp_history;
DROP POLICY IF EXISTS "Users can insert own xp_history" ON public.xp_history;
DROP POLICY IF EXISTS "Users can insert xp history" ON public.xp_history;

-- Badges table
DROP POLICY IF EXISTS "Badges are viewable by everyone" ON public.badges;

-- Milestones table
DROP POLICY IF EXISTS "Milestones are viewable by everyone" ON public.milestones;

-- User badges table
DROP POLICY IF EXISTS "Users can view all unlocked badges" ON public.user_badges;
DROP POLICY IF EXISTS "Users can insert badges" ON public.user_badges;
DROP POLICY IF EXISTS "Users can insert own badges" ON public.user_badges;
DROP POLICY IF EXISTS "Users can update own badges" ON public.user_badges;

-- User milestones table
DROP POLICY IF EXISTS "Users can view all milestone achievements" ON public.user_milestones;
DROP POLICY IF EXISTS "Users can insert milestones" ON public.user_milestones;
DROP POLICY IF EXISTS "Users can insert own milestones" ON public.user_milestones;

-- =============================================================================
-- STEP 2: CREATE PRODUCTION POLICIES (AUTHENTICATED USERS ONLY)
-- =============================================================================

-- =============================================================================
-- USERS TABLE POLICIES
-- =============================================================================

-- Public profiles viewable by everyone (for leaderboard)
CREATE POLICY "Public profiles are viewable by everyone"
  ON public.users
  FOR SELECT
  USING (true);

-- Only authenticated users can insert their profile
CREATE POLICY "Users can insert own profile"
  ON public.users
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- Only authenticated users can update their profile
CREATE POLICY "Users can update own profile"
  ON public.users
  FOR UPDATE
  USING (auth.uid()::text = user_id)
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- PROGRESS TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view own progress"
  ON public.progress
  FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own progress"
  ON public.progress
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own progress"
  ON public.progress
  FOR UPDATE
  USING (auth.uid()::text = user_id);

-- =============================================================================
-- XP_LOGS TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view own xp_logs"
  ON public.xp_logs
  FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own xp_logs"
  ON public.xp_logs
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- QUIZ_RESULTS TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view own quiz_results"
  ON public.quiz_results
  FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own quiz_results"
  ON public.quiz_results
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- QUIZ_SCORES TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view own quiz_scores"
  ON public.quiz_scores
  FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own quiz_scores"
  ON public.quiz_scores
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- USER_TOPICS TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view own user_topics"
  ON public.user_topics
  FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own user_topics"
  ON public.user_topics
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own user_topics"
  ON public.user_topics
  FOR UPDATE
  USING (auth.uid()::text = user_id);

-- =============================================================================
-- XP_HISTORY TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view own xp_history"
  ON public.xp_history
  FOR SELECT
  USING (auth.uid()::text = user_id);

CREATE POLICY "Users can insert own xp_history"
  ON public.xp_history
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- BADGES TABLE POLICIES (Public reference data)
-- =============================================================================

CREATE POLICY "Badges are viewable by everyone"
  ON public.badges
  FOR SELECT
  USING (true);

-- =============================================================================
-- MILESTONES TABLE POLICIES (Public reference data)
-- =============================================================================

CREATE POLICY "Milestones are viewable by everyone"
  ON public.milestones
  FOR SELECT
  USING (true);

-- =============================================================================
-- USER_BADGES TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view all unlocked badges"
  ON public.user_badges
  FOR SELECT
  USING (true);  -- Public for leaderboard/achievements page

CREATE POLICY "Users can insert own badges"
  ON public.user_badges
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own badges"
  ON public.user_badges
  FOR UPDATE
  USING (auth.uid()::text = user_id)
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- USER_MILESTONES TABLE POLICIES
-- =============================================================================

CREATE POLICY "Users can view all milestone achievements"
  ON public.user_milestones
  FOR SELECT
  USING (true);  -- Public for leaderboard/achievements page

CREATE POLICY "Users can insert own milestones"
  ON public.user_milestones
  FOR INSERT
  WITH CHECK (auth.uid()::text = user_id);

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify all policies are in place
SELECT 
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- =============================================================================
-- PRODUCTION CHECKLIST
-- =============================================================================

/*
✅ Before running this migration in production:

1. Ensure all users are authenticated via Supabase Auth
2. Remove all hardcoded 'demo_user' from backend code
3. Update frontend to require login
4. Test authentication flow thoroughly
5. Backup your database

⚠️ After running this migration:
- demo_user will NO LONGER have access
- Only authenticated users can access their own data
- Unauthenticated requests will be blocked by RLS

🧪 Test with:
-- Should work (authenticated user)
SELECT * FROM progress WHERE user_id = auth.uid()::text;

-- Should return empty (different user)
SELECT * FROM progress WHERE user_id = 'other_user_id';
*/
