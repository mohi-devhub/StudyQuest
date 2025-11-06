-- ===========================================================================
-- MIGRATION: User Feedback System
-- ===========================================================================
-- This migration adds a feedback collection system for beta testing
-- Run this in Supabase SQL Editor
-- ===========================================================================

-- =============================================================================
-- TABLE: user_feedback
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.user_feedback (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  category TEXT NOT NULL,  -- 'ux', 'speed', 'accuracy', 'motivation', 'general'
  comments TEXT,
  page_context TEXT,  -- Which page they were on
  session_metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.user_feedback IS 'User feedback and ratings for beta testing';
COMMENT ON COLUMN public.user_feedback.rating IS 'Rating from 1 (poor) to 5 (excellent)';
COMMENT ON COLUMN public.user_feedback.category IS 'Feedback category: ux, speed, accuracy, motivation, general';
COMMENT ON COLUMN public.user_feedback.comments IS 'User comments and suggestions';
COMMENT ON COLUMN public.user_feedback.page_context IS 'Page or feature being reviewed';
COMMENT ON COLUMN public.user_feedback.session_metadata IS 'Browser info, journey data, etc.';

-- =============================================================================
-- INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_user_feedback_user_id ON public.user_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_user_feedback_rating ON public.user_feedback(rating);
CREATE INDEX IF NOT EXISTS idx_user_feedback_category ON public.user_feedback(category);
CREATE INDEX IF NOT EXISTS idx_user_feedback_created ON public.user_feedback(created_at DESC);

-- =============================================================================
-- RLS POLICIES
-- =============================================================================
ALTER TABLE public.user_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Feedback is viewable by everyone"
  ON public.user_feedback FOR SELECT USING (true);

CREATE POLICY "Users can insert their own feedback"
  ON public.user_feedback FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update their own feedback"
  ON public.user_feedback FOR UPDATE USING (true);

-- =============================================================================
-- TABLE: beta_testers
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.beta_testers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL UNIQUE,
  email TEXT,
  name TEXT,
  invited_at TIMESTAMPTZ DEFAULT NOW(),
  started_testing_at TIMESTAMPTZ,
  completed_testing_at TIMESTAMPTZ,
  testing_status TEXT DEFAULT 'invited',  -- 'invited', 'active', 'completed'
  topics_studied INTEGER DEFAULT 0,
  quizzes_taken INTEGER DEFAULT 0,
  feedback_count INTEGER DEFAULT 0,
  notes TEXT,  -- Internal notes about this tester
  metadata JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE public.beta_testers IS 'Beta testing program participants';
COMMENT ON COLUMN public.beta_testers.testing_status IS 'Status: invited, active, completed';

-- =============================================================================
-- INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_beta_testers_user_id ON public.beta_testers(user_id);
CREATE INDEX IF NOT EXISTS idx_beta_testers_status ON public.beta_testers(testing_status);

-- =============================================================================
-- RLS POLICIES
-- =============================================================================
ALTER TABLE public.beta_testers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Beta testers are viewable by everyone"
  ON public.beta_testers FOR SELECT USING (true);

CREATE POLICY "Beta testers can update their own record"
  ON public.beta_testers FOR UPDATE USING (true);

-- =============================================================================
-- VIEW: Feedback Summary
-- =============================================================================
CREATE OR REPLACE VIEW public.feedback_summary AS
SELECT 
  category,
  COUNT(*) as total_responses,
  ROUND(AVG(rating), 2) as avg_rating,
  COUNT(*) FILTER (WHERE rating >= 4) as positive_count,
  COUNT(*) FILTER (WHERE rating <= 2) as negative_count,
  ARRAY_AGG(DISTINCT user_id) as unique_users
FROM public.user_feedback
GROUP BY category;

COMMENT ON VIEW public.feedback_summary IS 'Summary statistics of user feedback by category';

-- =============================================================================
-- VIEW: Beta Testing Progress
-- =============================================================================
CREATE OR REPLACE VIEW public.beta_testing_progress AS
SELECT 
  bt.user_id,
  bt.name,
  bt.testing_status,
  bt.invited_at,
  bt.started_testing_at,
  bt.completed_testing_at,
  COUNT(DISTINCT ut.topic) as unique_topics_studied,
  COUNT(DISTINCT qs.id) as quizzes_completed,
  COUNT(DISTINCT uf.id) as feedback_submitted,
  ROUND(AVG(qs.score), 2) as avg_quiz_score,
  MAX(qs.completed_at) as last_quiz_at,
  MAX(uf.created_at) as last_feedback_at
FROM public.beta_testers bt
LEFT JOIN public.user_topics ut ON ut.user_id = bt.user_id
LEFT JOIN public.quiz_scores qs ON qs.user_id = bt.user_id
LEFT JOIN public.user_feedback uf ON uf.user_id = bt.user_id
GROUP BY bt.user_id, bt.name, bt.testing_status, bt.invited_at, bt.started_testing_at, bt.completed_testing_at;

COMMENT ON VIEW public.beta_testing_progress IS 'Detailed progress tracking for beta testers';

-- =============================================================================
-- FUNCTION: Update Beta Tester Stats
-- =============================================================================
CREATE OR REPLACE FUNCTION update_beta_tester_stats()
RETURNS TRIGGER AS $$
BEGIN
  -- Update beta tester stats when feedback is submitted
  UPDATE public.beta_testers
  SET 
    feedback_count = (SELECT COUNT(*) FROM public.user_feedback WHERE user_id = NEW.user_id),
    testing_status = CASE 
      WHEN testing_status = 'invited' THEN 'active'
      ELSE testing_status
    END,
    started_testing_at = COALESCE(started_testing_at, NOW())
  WHERE user_id = NEW.user_id;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_feedback_submitted
  AFTER INSERT ON public.user_feedback
  FOR EACH ROW
  EXECUTE FUNCTION update_beta_tester_stats();

-- =============================================================================
-- SEED DATA: Sample Beta Testers (Optional)
-- =============================================================================
INSERT INTO public.beta_testers (user_id, email, name, testing_status, notes)
VALUES 
  ('beta_tester_1', 'alice@example.com', 'Alice Johnson', 'invited', 'UX designer with education background'),
  ('beta_tester_2', 'bob@example.com', 'Bob Smith', 'invited', 'College student, computer science major'),
  ('beta_tester_3', 'carol@example.com', 'Carol Davis', 'invited', 'High school teacher, tech-savvy'),
  ('beta_tester_4', 'david@example.com', 'David Lee', 'invited', 'Self-learner, interested in programming'),
  ('beta_tester_5', 'eve@example.com', 'Eve Martinez', 'invited', 'Bootcamp graduate, career switcher')
ON CONFLICT (user_id) DO NOTHING;

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Check tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
AND tablename IN ('user_feedback', 'beta_testers');

-- View feedback summary
SELECT * FROM public.feedback_summary;

-- View beta testing progress
SELECT * FROM public.beta_testing_progress;

-- Check sample beta testers
SELECT user_id, name, testing_status, invited_at 
FROM public.beta_testers 
ORDER BY invited_at;

-- =============================================================================
-- CLEANUP FUNCTION (for testing)
-- =============================================================================
CREATE OR REPLACE FUNCTION reset_beta_testing()
RETURNS void AS $$
BEGIN
  DELETE FROM public.user_feedback;
  DELETE FROM public.beta_testers;
  RAISE NOTICE 'Beta testing data reset complete';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- MIGRATION COMPLETE! ✅
-- =============================================================================
