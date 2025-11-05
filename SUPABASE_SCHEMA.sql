-- ===========================================================================
-- SUPABASE DATABASE SCHEMA FOR STUDYQUEST
-- ===========================================================================
-- Complete schema including all required tables for real-time features
-- Run this in your Supabase SQL Editor: https://app.supabase.com/project/_/sql
-- ===========================================================================

-- =============================================================================
-- USERS TABLE
-- =============================================================================
-- Note: Supabase provides auth.users by default, but we need a public.users 
-- table for additional user data and real-time updates
CREATE TABLE IF NOT EXISTS public.users (
  user_id TEXT PRIMARY KEY,  -- Using TEXT for demo_user compatibility
  username TEXT NOT NULL UNIQUE,
  email TEXT,
  total_xp INTEGER DEFAULT 0,
  level INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.users IS 'Extended user profile data for gamification';
COMMENT ON COLUMN public.users.total_xp IS 'Total experience points earned';
COMMENT ON COLUMN public.users.level IS 'Current level (500 XP per level)';

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- RLS Policies for users table
CREATE POLICY "Public profiles are viewable by everyone"
  ON public.users
  FOR SELECT
  USING (true);  -- Everyone can read leaderboard data

CREATE POLICY "Users can insert own profile"
  ON public.users
  FOR INSERT
  WITH CHECK (true);  -- Allow profile creation

CREATE POLICY "Users can update own profile"
  ON public.users
  FOR UPDATE
  USING (true)  -- For now, allow all updates (service role)
  WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON public.users(username);
CREATE INDEX IF NOT EXISTS idx_users_total_xp ON public.users(total_xp DESC);
CREATE INDEX IF NOT EXISTS idx_users_level ON public.users(level DESC);

-- =============================================================================
-- PROGRESS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,  -- Using TEXT for demo_user compatibility
  topic TEXT NOT NULL,
  avg_score DECIMAL(5,2) DEFAULT 0.0,
  quizzes_completed INTEGER DEFAULT 0,
  last_completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, topic)
);

COMMENT ON TABLE public.progress IS 'Tracks user progress for each study topic';
COMMENT ON COLUMN public.progress.avg_score IS 'Average quiz score as percentage (0.00 - 100.00)';
COMMENT ON COLUMN public.progress.quizzes_completed IS 'Number of quizzes completed for this topic';

-- Enable Row Level Security
ALTER TABLE public.progress ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view all progress"
  ON public.progress
  FOR SELECT
  USING (true);

CREATE POLICY "Users can insert progress"
  ON public.progress
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Users can update progress"
  ON public.progress
  FOR UPDATE
  USING (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON public.progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_topic ON public.progress(topic);
CREATE INDEX IF NOT EXISTS idx_progress_user_topic ON public.progress(user_id, topic);

-- =============================================================================
-- XP_LOGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.xp_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,  -- Using TEXT for demo_user compatibility
  xp_amount INTEGER NOT NULL,
  source TEXT NOT NULL,  -- 'quiz_complete', 'first_attempt', 'perfect_score', etc.
  topic TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.xp_logs IS 'Tracks all XP-earning activities for gamification';
COMMENT ON COLUMN public.xp_logs.source IS 'Activity type: quiz_complete, first_attempt, perfect_score, etc.';
COMMENT ON COLUMN public.xp_logs.metadata IS 'Additional data like quiz score, difficulty, etc.';

-- Enable Row Level Security
ALTER TABLE public.xp_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view all xp logs"
  ON public.xp_logs
  FOR SELECT
  USING (true);

CREATE POLICY "Users can insert xp logs"
  ON public.xp_logs
  FOR INSERT
  WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_id ON public.xp_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_xp_logs_created_at ON public.xp_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_created ON public.xp_logs(user_id, created_at DESC);

-- =============================================================================
-- QUIZ_RESULTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.quiz_results (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  difficulty TEXT NOT NULL,  -- 'beginner', 'intermediate', 'advanced', 'expert'
  score DECIMAL(5,2) NOT NULL,  -- Percentage score (0.00 - 100.00)
  total_questions INTEGER NOT NULL,
  correct_answers INTEGER NOT NULL,
  time_taken INTEGER,  -- Seconds
  xp_earned INTEGER DEFAULT 0,
  completed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.quiz_results IS 'Stores quiz completion data';
COMMENT ON COLUMN public.quiz_results.difficulty IS 'Quiz difficulty level';
COMMENT ON COLUMN public.quiz_results.score IS 'Quiz score as percentage';
COMMENT ON COLUMN public.quiz_results.xp_earned IS 'XP points earned from this quiz';

-- Enable Row Level Security
ALTER TABLE public.quiz_results ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view all quiz results"
  ON public.quiz_results
  FOR SELECT
  USING (true);

CREATE POLICY "Users can insert quiz results"
  ON public.quiz_results
  FOR INSERT
  WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_quiz_results_user_id ON public.quiz_results(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_results_topic ON public.quiz_results(topic);
CREATE INDEX IF NOT EXISTS idx_quiz_results_completed_at ON public.quiz_results(completed_at DESC);

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update users.updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_users_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_users_updated ON public.users;
CREATE TRIGGER on_users_updated
  BEFORE UPDATE ON public.users
  FOR EACH ROW
  EXECUTE FUNCTION public.update_users_timestamp();

-- Auto-update progress.updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_progress_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_progress_updated ON public.progress;
CREATE TRIGGER on_progress_updated
  BEFORE UPDATE ON public.progress
  FOR EACH ROW
  EXECUTE FUNCTION public.update_progress_timestamp();

-- =============================================================================
-- ENABLE REALTIME
-- =============================================================================
-- Enable realtime for all tables needed for live updates

ALTER PUBLICATION supabase_realtime ADD TABLE public.users;
ALTER PUBLICATION supabase_realtime ADD TABLE public.progress;
ALTER PUBLICATION supabase_realtime ADD TABLE public.xp_logs;
ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_results;

-- =============================================================================
-- SEED DATA
-- =============================================================================
-- Insert demo user for testing
INSERT INTO public.users (user_id, username, total_xp, level, email)
VALUES 
  ('demo_user', 'demo_user', 2450, 5, 'demo@studyquest.com')
ON CONFLICT (username) DO NOTHING;

-- Insert some demo progress
INSERT INTO public.progress (user_id, topic, avg_score, quizzes_completed, last_completed_at)
VALUES
  ('demo_user', 'JavaScript Basics', 85.50, 12, NOW() - INTERVAL '1 day'),
  ('demo_user', 'Python Fundamentals', 92.30, 8, NOW() - INTERVAL '2 days'),
  ('demo_user', 'React Hooks', 78.00, 5, NOW() - INTERVAL '3 days'),
  ('demo_user', 'SQL Queries', 88.75, 10, NOW() - INTERVAL '4 days')
ON CONFLICT (user_id, topic) DO NOTHING;

-- Insert some demo XP logs
INSERT INTO public.xp_logs (user_id, xp_amount, source, topic, created_at)
VALUES
  ('demo_user', 150, 'quiz_complete', 'JavaScript Basics', NOW() - INTERVAL '1 day'),
  ('demo_user', 200, 'perfect_score', 'Python Fundamentals', NOW() - INTERVAL '2 days'),
  ('demo_user', 165, 'quiz_complete', 'React Hooks', NOW() - INTERVAL '3 days'),
  ('demo_user', 180, 'quiz_complete', 'SQL Queries', NOW() - INTERVAL '4 days');

-- Insert demo leaderboard users
INSERT INTO public.users (user_id, username, total_xp, level, email)
VALUES
  ('user_1', 'CodeMaster3000', 5420, 11, 'codemaster@example.com'),
  ('user_2', 'AlgoWizard', 4890, 10, 'algo@example.com'),
  ('user_3', 'PyThOnPrO', 4250, 9, 'python@example.com'),
  ('user_4', 'DataNinja42', 3870, 8, 'data@example.com'),
  ('user_5', 'JSWarrior', 3250, 7, 'js@example.com'),
  ('user_6', 'SQLSensei', 2980, 6, 'sql@example.com'),
  ('user_7', 'ReactRanger', 2100, 5, 'react@example.com'),
  ('user_8', 'TypeMaster', 1890, 4, 'type@example.com'),
  ('user_9', 'DevGuru99', 1450, 3, 'dev@example.com')
ON CONFLICT (username) DO NOTHING;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- Run these to verify the setup:

-- Check tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
AND tablename IN ('users', 'progress', 'xp_logs', 'quiz_results');

-- Check RLS is enabled
SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public'
AND tablename IN ('users', 'progress', 'xp_logs', 'quiz_results');

-- Check realtime is enabled
SELECT schemaname, tablename FROM pg_publication_tables 
WHERE pubname = 'supabase_realtime';

-- View demo data
SELECT * FROM public.users ORDER BY total_xp DESC LIMIT 5;
SELECT * FROM public.progress WHERE user_id = 'demo_user';
SELECT * FROM public.xp_logs WHERE user_id = 'demo_user' ORDER BY created_at DESC LIMIT 5;

-- =============================================================================
-- COMPLETE! 🎉
-- =============================================================================
-- All tables created, RLS enabled, realtime configured, and demo data inserted.
-- Next steps:
-- 1. Restart your Next.js dev server
-- 2. Visit http://localhost:3001
-- 3. Check the dashboard for real-time connection status
-- 4. Visit /leaderboard to see live rankings
-- =============================================================================
