-- =====================================================
-- MIGRATION: Study Sessions Table
-- =====================================================
-- This migration adds a table to store AI-generated study notes
-- so users can select from previously generated content
-- Run this in Supabase SQL Editor
-- =====================================================

-- =============================================================================
-- TABLE: study_sessions
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.study_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  summary TEXT NOT NULL,
  key_points JSONB NOT NULL DEFAULT '[]'::jsonb,
  quiz_questions JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.study_sessions IS 'Stores AI-generated study notes and quizzes';
COMMENT ON COLUMN public.study_sessions.user_id IS 'User who created the study session';
COMMENT ON COLUMN public.study_sessions.topic IS 'Study topic';
COMMENT ON COLUMN public.study_sessions.summary IS 'AI-generated summary';
COMMENT ON COLUMN public.study_sessions.key_points IS 'Array of key learning points';
COMMENT ON COLUMN public.study_sessions.quiz_questions IS 'Generated quiz questions';

-- Enable Row Level Security
ALTER TABLE public.study_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own study sessions"
  ON public.study_sessions
  FOR SELECT
  USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can insert own study sessions"
  ON public.study_sessions
  FOR INSERT
  WITH CHECK (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can update own study sessions"
  ON public.study_sessions
  FOR UPDATE
  USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

CREATE POLICY "Users can delete own study sessions"
  ON public.study_sessions
  FOR DELETE
  USING (user_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON public.study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_created_at ON public.study_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_study_sessions_topic ON public.study_sessions(topic);

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_study_session_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS on_study_session_updated ON public.study_sessions;
CREATE TRIGGER on_study_session_updated
  BEFORE UPDATE ON public.study_sessions
  FOR EACH ROW
  EXECUTE FUNCTION public.update_study_session_timestamp();

-- Enable realtime for live updates
ALTER PUBLICATION supabase_realtime ADD TABLE public.study_sessions;

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- Verify table was created
SELECT 
  tablename, 
  rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename = 'study_sessions';

-- View table structure
SELECT 
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
AND table_name = 'study_sessions'
ORDER BY ordinal_position;

-- =============================================================================
-- COMPLETE! 🎉
-- =============================================================================
-- Study sessions table is ready to store AI-generated notes
-- Users can now select from previously generated study materials
-- =============================================================================
