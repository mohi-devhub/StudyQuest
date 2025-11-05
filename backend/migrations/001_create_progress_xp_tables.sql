-- Migration: Create progress and xp_logs tables
-- Created: 2025-11-05
-- Description: Progress tracking and XP system for StudyQuest

-- =============================================================================
-- PROGRESS TABLE
-- =============================================================================
-- Tracks user progress for each study topic
CREATE TABLE IF NOT EXISTS public.progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  topic TEXT NOT NULL,
  completion_status TEXT NOT NULL DEFAULT 'not_started',
  last_attempt TIMESTAMPTZ,
  avg_score DECIMAL(5,2) DEFAULT 0.0,
  total_attempts INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, topic)
);

-- Add comments for documentation
COMMENT ON TABLE public.progress IS 'Tracks user progress for each study topic';
COMMENT ON COLUMN public.progress.completion_status IS 'Status: not_started, in_progress, completed';
COMMENT ON COLUMN public.progress.avg_score IS 'Average quiz score as percentage (0.00 - 100.00)';
COMMENT ON COLUMN public.progress.total_attempts IS 'Number of times user attempted quizzes for this topic';

-- Enable Row Level Security
ALTER TABLE public.progress ENABLE ROW LEVEL SECURITY;

-- RLS Policies for progress table
CREATE POLICY "Users can view own progress"
  ON public.progress
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own progress"
  ON public.progress
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own progress"
  ON public.progress
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own progress"
  ON public.progress
  FOR DELETE
  USING (auth.uid() = user_id);

-- =============================================================================
-- XP_LOGS TABLE
-- =============================================================================
-- Tracks all XP-earning activities for gamification
CREATE TABLE IF NOT EXISTS public.xp_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  points INTEGER NOT NULL,
  reason TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE public.xp_logs IS 'Tracks all XP-earning activities for gamification';
COMMENT ON COLUMN public.xp_logs.reason IS 'Activity type: quiz_completed, study_session, daily_streak, etc.';
COMMENT ON COLUMN public.xp_logs.metadata IS 'Additional data like quiz score, topic, session duration, etc.';

-- Enable Row Level Security
ALTER TABLE public.xp_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for xp_logs table
CREATE POLICY "Users can view own xp logs"
  ON public.xp_logs
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own xp logs"
  ON public.xp_logs
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Note: For backend insertion using service role key, RLS is bypassed automatically

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON public.progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_topic ON public.progress(topic);
CREATE INDEX IF NOT EXISTS idx_progress_user_topic ON public.progress(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_progress_completion_status ON public.progress(completion_status);

CREATE INDEX IF NOT EXISTS idx_xp_logs_user_id ON public.xp_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_xp_logs_timestamp ON public.xp_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_timestamp ON public.xp_logs(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_xp_logs_reason ON public.xp_logs(reason);

-- =============================================================================
-- TRIGGERS
-- =============================================================================
-- Auto-update updated_at timestamp on progress changes
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
-- VIEWS
-- =============================================================================
-- View to get total XP per user
CREATE OR REPLACE VIEW public.user_total_xp AS
SELECT 
  user_id,
  SUM(points) as total_xp,
  COUNT(*) as total_activities,
  MAX(timestamp) as last_activity
FROM public.xp_logs
GROUP BY user_id;

COMMENT ON VIEW public.user_total_xp IS 'Aggregated XP statistics per user';

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================
-- Function to update progress after quiz completion
CREATE OR REPLACE FUNCTION public.update_progress_after_quiz(
  p_user_id UUID,
  p_topic TEXT,
  p_score DECIMAL,
  p_completion_status TEXT DEFAULT 'in_progress'
)
RETURNS void AS $$
DECLARE
  current_avg DECIMAL;
  current_attempts INTEGER;
  new_avg DECIMAL;
BEGIN
  -- Get current stats
  SELECT avg_score, total_attempts 
  INTO current_avg, current_attempts
  FROM public.progress
  WHERE user_id = p_user_id AND topic = p_topic;
  
  -- Calculate new average
  IF current_attempts IS NULL OR current_attempts = 0 THEN
    new_avg := p_score;
    current_attempts := 0;
  ELSE
    new_avg := ((current_avg * current_attempts) + p_score) / (current_attempts + 1);
  END IF;
  
  -- Insert or update progress
  INSERT INTO public.progress (user_id, topic, completion_status, last_attempt, avg_score, total_attempts)
  VALUES (p_user_id, p_topic, p_completion_status, NOW(), new_avg, current_attempts + 1)
  ON CONFLICT (user_id, topic) 
  DO UPDATE SET
    completion_status = EXCLUDED.completion_status,
    last_attempt = EXCLUDED.last_attempt,
    avg_score = EXCLUDED.avg_score,
    total_attempts = EXCLUDED.total_attempts;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.update_progress_after_quiz IS 'Updates user progress with new quiz score and calculates running average';

-- Function to award XP points
CREATE OR REPLACE FUNCTION public.award_xp(
  p_user_id UUID,
  p_points INTEGER,
  p_reason TEXT,
  p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
  new_log_id UUID;
BEGIN
  INSERT INTO public.xp_logs (user_id, points, reason, metadata)
  VALUES (p_user_id, p_points, p_reason, p_metadata)
  RETURNING id INTO new_log_id;
  
  RETURN new_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION public.award_xp IS 'Awards XP points to a user for a specific reason';

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- Run these after migration to verify setup:
-- 
-- SELECT tablename, schemaname FROM pg_tables WHERE schemaname = 'public' AND tablename IN ('progress', 'xp_logs');
-- SELECT * FROM pg_policies WHERE tablename IN ('progress', 'xp_logs');
-- SELECT indexname, indexdef FROM pg_indexes WHERE schemaname = 'public' AND tablename IN ('progress', 'xp_logs');
