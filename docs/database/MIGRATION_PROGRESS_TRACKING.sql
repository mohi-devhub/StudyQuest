-- ===========================================================================
-- MIGRATION: Enhanced Progress Tracking Schema
-- ===========================================================================
-- This migration extends the existing schema with additional tables for
-- detailed progress tracking and XP history
-- Run this in Supabase SQL Editor after the main schema is set up
-- ===========================================================================

-- =============================================================================
-- NEW TABLE: user_topics
-- =============================================================================
-- Tracks user engagement with specific topics, including current status
CREATE TABLE IF NOT EXISTS public.user_topics (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'not_started',  -- 'not_started', 'in_progress', 'completed', 'mastered'
  score DECIMAL(5,2) DEFAULT 0.0,  -- Latest quiz score (0.00 - 100.00)
  best_score DECIMAL(5,2) DEFAULT 0.0,  -- Best score achieved
  attempts INTEGER DEFAULT 0,  -- Number of quiz attempts
  time_spent INTEGER DEFAULT 0,  -- Total time spent in seconds
  last_attempted_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,  -- When status changed to 'completed'
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, topic)
);

COMMENT ON TABLE public.user_topics IS 'Detailed tracking of user engagement with each topic';
COMMENT ON COLUMN public.user_topics.status IS 'Current status: not_started, in_progress, completed, mastered';
COMMENT ON COLUMN public.user_topics.score IS 'Latest quiz score as percentage';
COMMENT ON COLUMN public.user_topics.best_score IS 'Best score achieved across all attempts';
COMMENT ON COLUMN public.user_topics.attempts IS 'Total number of quiz attempts for this topic';
COMMENT ON COLUMN public.user_topics.time_spent IS 'Cumulative time spent on this topic in seconds';

-- Enable Row Level Security
ALTER TABLE public.user_topics ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view all topics"
  ON public.user_topics FOR SELECT USING (true);

CREATE POLICY "Users can insert topics"
  ON public.user_topics FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update topics"
  ON public.user_topics FOR UPDATE USING (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_topics_user_id ON public.user_topics(user_id);
CREATE INDEX IF NOT EXISTS idx_user_topics_status ON public.user_topics(status);
CREATE INDEX IF NOT EXISTS idx_user_topics_user_status ON public.user_topics(user_id, status);
CREATE INDEX IF NOT EXISTS idx_user_topics_score ON public.user_topics(best_score DESC);

-- =============================================================================
-- NEW TABLE: quiz_scores
-- =============================================================================
-- Detailed individual quiz attempt records
CREATE TABLE IF NOT EXISTS public.quiz_scores (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  difficulty TEXT NOT NULL DEFAULT 'medium',  -- 'easy', 'medium', 'hard', 'expert'
  correct INTEGER NOT NULL,  -- Number of correct answers
  total INTEGER NOT NULL,  -- Total number of questions
  score DECIMAL(5,2) NOT NULL,  -- Calculated percentage score
  xp_gained INTEGER DEFAULT 0,  -- XP points earned from this quiz
  time_taken INTEGER,  -- Time in seconds
  answers JSONB DEFAULT '[]'::jsonb,  -- Array of user answers
  questions JSONB DEFAULT '[]'::jsonb,  -- Quiz questions for reference
  metadata JSONB DEFAULT '{}'::jsonb,  -- Additional data (streak, bonuses, etc.)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.quiz_scores IS 'Individual quiz attempt records with detailed scoring';
COMMENT ON COLUMN public.quiz_scores.correct IS 'Number of questions answered correctly';
COMMENT ON COLUMN public.quiz_scores.total IS 'Total number of questions in the quiz';
COMMENT ON COLUMN public.quiz_scores.score IS 'Percentage score (correct/total * 100)';
COMMENT ON COLUMN public.quiz_scores.answers IS 'Array of user answers for review';
COMMENT ON COLUMN public.quiz_scores.questions IS 'Quiz questions snapshot for historical reference';

-- Enable Row Level Security
ALTER TABLE public.quiz_scores ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view all quiz scores"
  ON public.quiz_scores FOR SELECT USING (true);

CREATE POLICY "Users can insert quiz scores"
  ON public.quiz_scores FOR INSERT WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_quiz_scores_user_id ON public.quiz_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_topic ON public.quiz_scores(topic);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_user_topic ON public.quiz_scores(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_created_at ON public.quiz_scores(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_score ON public.quiz_scores(score DESC);

-- =============================================================================
-- NEW TABLE: xp_history
-- =============================================================================
-- Comprehensive XP change log with reasons
CREATE TABLE IF NOT EXISTS public.xp_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  xp_change INTEGER NOT NULL,  -- Can be positive or negative
  reason TEXT NOT NULL,  -- 'quiz_complete', 'daily_bonus', 'achievement', 'penalty', etc.
  topic TEXT,  -- Optional: related topic
  quiz_id UUID,  -- Optional: reference to quiz_scores
  previous_xp INTEGER NOT NULL,  -- XP before change
  new_xp INTEGER NOT NULL,  -- XP after change
  previous_level INTEGER,  -- Level before change
  new_level INTEGER,  -- Level after change (for level-up tracking)
  metadata JSONB DEFAULT '{}'::jsonb,  -- Additional context
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.xp_history IS 'Complete history of all XP changes with before/after tracking';
COMMENT ON COLUMN public.xp_history.xp_change IS 'XP delta (positive for gains, negative for penalties)';
COMMENT ON COLUMN public.xp_history.reason IS 'Why XP changed: quiz_complete, achievement, daily_bonus, etc.';
COMMENT ON COLUMN public.xp_history.previous_xp IS 'Total XP before this change';
COMMENT ON COLUMN public.xp_history.new_xp IS 'Total XP after this change';

-- Enable Row Level Security
ALTER TABLE public.xp_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view all xp history"
  ON public.xp_history FOR SELECT USING (true);

CREATE POLICY "Users can insert xp history"
  ON public.xp_history FOR INSERT WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_xp_history_user_id ON public.xp_history(user_id);
CREATE INDEX IF NOT EXISTS idx_xp_history_created_at ON public.xp_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_xp_history_user_created ON public.xp_history(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_xp_history_reason ON public.xp_history(reason);
CREATE INDEX IF NOT EXISTS idx_xp_history_quiz_id ON public.xp_history(quiz_id);

-- =============================================================================
-- TRIGGERS FOR AUTO-UPDATES
-- =============================================================================

-- Auto-update user_topics.updated_at
CREATE OR REPLACE FUNCTION public.update_user_topics_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_user_topics_updated ON public.user_topics;
CREATE TRIGGER on_user_topics_updated
  BEFORE UPDATE ON public.user_topics
  FOR EACH ROW
  EXECUTE FUNCTION public.update_user_topics_timestamp();

-- Auto-calculate score percentage when quiz_scores inserted
CREATE OR REPLACE FUNCTION public.calculate_quiz_score()
RETURNS TRIGGER AS $$
BEGIN
  -- Calculate percentage if not provided
  IF NEW.score IS NULL OR NEW.score = 0 THEN
    NEW.score = ROUND((NEW.correct::DECIMAL / NULLIF(NEW.total, 0)::DECIMAL) * 100, 2);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_quiz_score_insert ON public.quiz_scores;
CREATE TRIGGER on_quiz_score_insert
  BEFORE INSERT ON public.quiz_scores
  FOR EACH ROW
  EXECUTE FUNCTION public.calculate_quiz_score();

-- Auto-update user_topics when quiz_scores inserted
CREATE OR REPLACE FUNCTION public.update_topic_progress()
RETURNS TRIGGER AS $$
DECLARE
  current_best DECIMAL(5,2);
  current_attempts INTEGER;
BEGIN
  -- Get current best score and attempts
  SELECT best_score, attempts INTO current_best, current_attempts
  FROM public.user_topics
  WHERE user_id = NEW.user_id AND topic = NEW.topic;
  
  -- Insert or update user_topics
  INSERT INTO public.user_topics (
    user_id, 
    topic, 
    score, 
    best_score, 
    attempts,
    status,
    last_attempted_at
  )
  VALUES (
    NEW.user_id,
    NEW.topic,
    NEW.score,
    GREATEST(NEW.score, COALESCE(current_best, 0)),
    COALESCE(current_attempts, 0) + 1,
    CASE 
      WHEN NEW.score >= 90 THEN 'mastered'
      WHEN NEW.score >= 70 THEN 'completed'
      ELSE 'in_progress'
    END,
    NOW()
  )
  ON CONFLICT (user_id, topic) 
  DO UPDATE SET
    score = NEW.score,
    best_score = GREATEST(NEW.score, public.user_topics.best_score),
    attempts = public.user_topics.attempts + 1,
    status = CASE 
      WHEN NEW.score >= 90 THEN 'mastered'
      WHEN NEW.score >= 70 THEN 'completed'
      WHEN public.user_topics.status = 'not_started' THEN 'in_progress'
      ELSE public.user_topics.status
    END,
    last_attempted_at = NOW(),
    completed_at = CASE 
      WHEN NEW.score >= 70 AND public.user_topics.completed_at IS NULL THEN NOW()
      ELSE public.user_topics.completed_at
    END;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_quiz_score_completed ON public.quiz_scores;
CREATE TRIGGER on_quiz_score_completed
  AFTER INSERT ON public.quiz_scores
  FOR EACH ROW
  EXECUTE FUNCTION public.update_topic_progress();

-- Auto-create xp_history entry when xp_logs inserted (for compatibility)
CREATE OR REPLACE FUNCTION public.sync_xp_to_history()
RETURNS TRIGGER AS $$
DECLARE
  user_total_xp INTEGER;
  user_level INTEGER;
BEGIN
  -- Get current user XP
  SELECT total_xp, level INTO user_total_xp, user_level
  FROM public.users
  WHERE user_id = NEW.user_id;
  
  -- Insert into xp_history
  INSERT INTO public.xp_history (
    user_id,
    xp_change,
    reason,
    topic,
    previous_xp,
    new_xp,
    previous_level,
    new_level,
    metadata,
    created_at
  )
  VALUES (
    NEW.user_id,
    NEW.xp_amount,
    NEW.source,
    NEW.topic,
    COALESCE(user_total_xp, 0) - NEW.xp_amount,  -- Previous XP
    COALESCE(user_total_xp, 0),  -- New XP
    COALESCE(user_level, 1),  -- Assuming no level change for now
    COALESCE(user_level, 1),
    NEW.metadata,
    NEW.created_at
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_xp_log_insert ON public.xp_logs;
CREATE TRIGGER on_xp_log_insert
  AFTER INSERT ON public.xp_logs
  FOR EACH ROW
  EXECUTE FUNCTION public.sync_xp_to_history();

-- =============================================================================
-- ENABLE REALTIME FOR NEW TABLES
-- =============================================================================
-- Skip if tables are already added to realtime publication
DO $$
BEGIN
  -- Add user_topics to realtime if not already added
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND schemaname = 'public' 
    AND tablename = 'user_topics'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.user_topics;
  END IF;
  
  -- Add quiz_scores to realtime if not already added
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND schemaname = 'public' 
    AND tablename = 'quiz_scores'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.quiz_scores;
  END IF;
  
  -- Add xp_history to realtime if not already added
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' 
    AND schemaname = 'public' 
    AND tablename = 'xp_history'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.xp_history;
  END IF;
END $$;

-- =============================================================================
-- UTILITY VIEWS
-- =============================================================================

-- View: User progress summary
CREATE OR REPLACE VIEW public.user_progress_summary AS
SELECT 
  ut.user_id,
  COUNT(*) as total_topics,
  COUNT(*) FILTER (WHERE status = 'mastered') as mastered_count,
  COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
  COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_count,
  ROUND(AVG(best_score), 2) as avg_best_score,
  SUM(attempts) as total_attempts,
  SUM(time_spent) as total_time_spent
FROM public.user_topics ut
GROUP BY ut.user_id;

COMMENT ON VIEW public.user_progress_summary IS 'Aggregated user progress statistics';

-- View: Recent quiz activity
CREATE OR REPLACE VIEW public.recent_quiz_activity AS
SELECT 
  qs.id,
  qs.user_id,
  u.username,
  qs.topic,
  qs.score,
  qs.xp_gained,
  qs.created_at
FROM public.quiz_scores qs
JOIN public.users u ON u.user_id = qs.user_id
ORDER BY qs.created_at DESC
LIMIT 100;

COMMENT ON VIEW public.recent_quiz_activity IS 'Recent quiz completions across all users';

-- View: XP leaderboard with details
CREATE OR REPLACE VIEW public.xp_leaderboard_detailed AS
SELECT 
  u.user_id,
  u.username,
  u.total_xp,
  u.level,
  COUNT(DISTINCT qs.topic) as topics_attempted,
  COUNT(qs.id) as total_quizzes,
  ROUND(AVG(qs.score), 2) as avg_score,
  MAX(qs.created_at) as last_quiz_at
FROM public.users u
LEFT JOIN public.quiz_scores qs ON qs.user_id = u.user_id
GROUP BY u.user_id, u.username, u.total_xp, u.level
ORDER BY u.total_xp DESC;

COMMENT ON VIEW public.xp_leaderboard_detailed IS 'Enhanced leaderboard with quiz statistics';

-- =============================================================================
-- SEED DATA FOR NEW TABLES
-- =============================================================================

-- Insert demo data for user_topics
INSERT INTO public.user_topics (user_id, topic, status, score, best_score, attempts, last_attempted_at)
VALUES
  ('demo_user', 'JavaScript Basics', 'mastered', 92.00, 95.00, 15, NOW() - INTERVAL '1 hour'),
  ('demo_user', 'Python Fundamentals', 'completed', 85.00, 88.00, 10, NOW() - INTERVAL '2 hours'),
  ('demo_user', 'React Hooks', 'in_progress', 68.00, 72.00, 7, NOW() - INTERVAL '5 hours'),
  ('demo_user', 'SQL Queries', 'mastered', 94.00, 96.00, 12, NOW() - INTERVAL '1 day')
ON CONFLICT (user_id, topic) DO NOTHING;

-- Insert demo quiz scores
INSERT INTO public.quiz_scores (user_id, topic, difficulty, correct, total, xp_gained, time_taken)
VALUES
  ('demo_user', 'JavaScript Basics', 'medium', 9, 10, 150, 240),
  ('demo_user', 'Python Fundamentals', 'medium', 8, 10, 140, 180),
  ('demo_user', 'React Hooks', 'hard', 7, 10, 160, 300),
  ('demo_user', 'SQL Queries', 'medium', 10, 10, 200, 150)
ON CONFLICT DO NOTHING;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Check new tables exist
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
AND tablename IN ('user_topics', 'quiz_scores', 'xp_history');

-- Check triggers exist
SELECT tgname FROM pg_trigger WHERE tgname IN (
  'on_user_topics_updated', 
  'on_quiz_score_insert', 
  'on_quiz_score_completed',
  'on_xp_log_insert'
);

-- View demo data
SELECT * FROM public.user_topics WHERE user_id = 'demo_user';
SELECT * FROM public.quiz_scores WHERE user_id = 'demo_user';
SELECT * FROM public.xp_history WHERE user_id = 'demo_user' ORDER BY created_at DESC LIMIT 5;

-- Check views
SELECT * FROM public.user_progress_summary WHERE user_id = 'demo_user';
SELECT * FROM public.recent_quiz_activity LIMIT 5;

-- =============================================================================
-- MIGRATION COMPLETE! 🎉
-- =============================================================================
-- New tables added:
--   ✓ user_topics - Detailed topic engagement tracking
--   ✓ quiz_scores - Individual quiz attempt records
--   ✓ xp_history - Complete XP change log
--
-- Features enabled:
--   ✓ Auto-calculation of quiz scores
--   ✓ Auto-update of topic progress on quiz completion
--   ✓ XP history syncing with xp_logs
--   ✓ Realtime updates for all new tables
--   ✓ Utility views for common queries
--
-- Next steps:
--   1. Update FastAPI routes to use new tables
--   2. Test quiz submission flow
--   3. Verify XP and progress auto-updates
-- =============================================================================
