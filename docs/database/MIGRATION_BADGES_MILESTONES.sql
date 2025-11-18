-- ===========================================================================
-- MIGRATION: Badge & Milestone System
-- ===========================================================================
-- This migration adds badge tracking and milestone achievements
-- Run this in Supabase SQL Editor after the progress tracking migration
-- ===========================================================================

-- =============================================================================
-- TABLE: badges (Master list of all available badges)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.badges (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  badge_key TEXT NOT NULL UNIQUE,  -- 'novice_scholar', 'curious_mind', etc.
  name TEXT NOT NULL,  -- Display name
  description TEXT NOT NULL,
  category TEXT NOT NULL,  -- 'level', 'quiz', 'streak', 'achievement'
  requirement_type TEXT NOT NULL,  -- 'level', 'total_xp', 'quizzes_completed', etc.
  requirement_value INTEGER NOT NULL,  -- Threshold to unlock
  symbol TEXT DEFAULT '[*]',  -- ASCII symbol
  tier INTEGER DEFAULT 1,  -- 1=bronze, 2=silver, 3=gold, 4=platinum
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.badges IS 'Master list of all available badges and their unlock requirements';
COMMENT ON COLUMN public.badges.badge_key IS 'Unique identifier for the badge';
COMMENT ON COLUMN public.badges.requirement_type IS 'What metric unlocks this badge';
COMMENT ON COLUMN public.badges.requirement_value IS 'Threshold value to unlock';
COMMENT ON COLUMN public.badges.tier IS '1=bronze, 2=silver, 3=gold, 4=platinum';

-- =============================================================================
-- TABLE: user_badges (User's unlocked badges)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.user_badges (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  badge_id UUID NOT NULL REFERENCES public.badges(id),
  unlocked_at TIMESTAMPTZ DEFAULT NOW(),
  seen BOOLEAN DEFAULT FALSE,  -- Has user seen the unlock notification?
  metadata JSONB DEFAULT '{}'::jsonb,  -- Additional unlock context
  UNIQUE(user_id, badge_id)
);

COMMENT ON TABLE public.user_badges IS 'Tracks which badges each user has unlocked';
COMMENT ON COLUMN public.user_badges.seen IS 'Whether user has viewed the unlock notification';
COMMENT ON COLUMN public.user_badges.metadata IS 'Context about unlock (e.g., which quiz triggered it)';

-- Enable Row Level Security
ALTER TABLE public.badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_badges ENABLE ROW LEVEL SECURITY;

-- RLS Policies for badges (public readable)
CREATE POLICY "Badges are viewable by everyone"
  ON public.badges FOR SELECT USING (true);

-- RLS Policies for user_badges
CREATE POLICY "Users can view all unlocked badges"
  ON public.user_badges FOR SELECT USING (true);

CREATE POLICY "Users can insert badges"
  ON public.user_badges FOR INSERT WITH CHECK (true);

CREATE POLICY "Users can update own badges"
  ON public.user_badges FOR UPDATE USING (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_badges_category ON public.badges(category);
CREATE INDEX IF NOT EXISTS idx_badges_requirement ON public.badges(requirement_type, requirement_value);
CREATE INDEX IF NOT EXISTS idx_user_badges_user_id ON public.user_badges(user_id);
CREATE INDEX IF NOT EXISTS idx_user_badges_unlocked_at ON public.user_badges(unlocked_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_badges_seen ON public.user_badges(user_id, seen) WHERE seen = FALSE;

-- =============================================================================
-- TABLE: milestones (Milestone tracking)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.milestones (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  milestone_key TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,  -- 'xp', 'quiz', 'streak', 'topic'
  threshold INTEGER NOT NULL,
  symbol TEXT DEFAULT '[!]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.milestones IS 'Milestone achievements (numeric thresholds)';
COMMENT ON COLUMN public.milestones.threshold IS 'Numeric threshold to achieve milestone';

-- =============================================================================
-- TABLE: user_milestones (User milestone progress)
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.user_milestones (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id TEXT NOT NULL,
  milestone_id UUID NOT NULL REFERENCES public.milestones(id),
  achieved_at TIMESTAMPTZ DEFAULT NOW(),
  current_value INTEGER NOT NULL,  -- Value when milestone was reached
  metadata JSONB DEFAULT '{}'::jsonb,
  UNIQUE(user_id, milestone_id)
);

COMMENT ON TABLE public.user_milestones IS 'Tracks milestone achievements per user';
COMMENT ON COLUMN public.user_milestones.current_value IS 'Metric value when milestone was achieved';

-- Enable RLS
ALTER TABLE public.milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_milestones ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Milestones are viewable by everyone"
  ON public.milestones FOR SELECT USING (true);

CREATE POLICY "Users can view all milestone achievements"
  ON public.user_milestones FOR SELECT USING (true);

CREATE POLICY "Users can insert milestones"
  ON public.user_milestones FOR INSERT WITH CHECK (true);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_milestones_user_id ON public.user_milestones(user_id);
CREATE INDEX IF NOT EXISTS idx_user_milestones_achieved ON public.user_milestones(achieved_at DESC);

-- =============================================================================
-- FUNCTION: Check and award badges
-- =============================================================================
CREATE OR REPLACE FUNCTION public.check_and_award_badges(
  p_user_id TEXT
)
RETURNS TABLE(
  badge_id UUID,
  badge_name TEXT,
  badge_symbol TEXT,
  newly_unlocked BOOLEAN
) AS $$
DECLARE
  user_stats RECORD;
  v_badge RECORD;
  existing_badge UUID;
BEGIN
  -- Get user statistics
  SELECT 
    u.total_xp,
    u.level,
    COUNT(DISTINCT qs.id) as total_quizzes,
    COUNT(DISTINCT ut.topic) FILTER (WHERE ut.status = 'mastered') as mastered_topics,
    COUNT(DISTINCT ut.topic) FILTER (WHERE ut.status IN ('completed', 'mastered')) as completed_topics
  INTO user_stats
  FROM public.users u
  LEFT JOIN public.quiz_scores qs ON qs.user_id = u.user_id
  LEFT JOIN public.user_topics ut ON ut.user_id = u.user_id
  WHERE u.user_id = p_user_id
  GROUP BY u.user_id, u.total_xp, u.level;

  -- Check each badge requirement
  FOR v_badge IN 
    SELECT * FROM public.badges 
    ORDER BY requirement_value ASC
  LOOP
    -- Check if user already has this badge
    SELECT ub.badge_id INTO existing_badge
    FROM public.user_badges ub
    WHERE ub.user_id = p_user_id AND ub.badge_id = v_badge.id;

    -- If badge not yet unlocked, check requirements
    IF existing_badge IS NULL THEN
      CASE v_badge.requirement_type
        WHEN 'level' THEN
          IF user_stats.level >= v_badge.requirement_value THEN
            INSERT INTO public.user_badges (user_id, badge_id, metadata)
            VALUES (p_user_id, v_badge.id, jsonb_build_object('level', user_stats.level));
            
            RETURN QUERY SELECT v_badge.id, v_badge.name, v_badge.symbol, TRUE;
          END IF;
          
        WHEN 'total_xp' THEN
          IF user_stats.total_xp >= v_badge.requirement_value THEN
            INSERT INTO public.user_badges (user_id, badge_id, metadata)
            VALUES (p_user_id, v_badge.id, jsonb_build_object('total_xp', user_stats.total_xp));
            
            RETURN QUERY SELECT v_badge.id, v_badge.name, v_badge.symbol, TRUE;
          END IF;
          
        WHEN 'quizzes_completed' THEN
          IF user_stats.total_quizzes >= v_badge.requirement_value THEN
            INSERT INTO public.user_badges (user_id, badge_id, metadata)
            VALUES (p_user_id, v_badge.id, jsonb_build_object('total_quizzes', user_stats.total_quizzes));
            
            RETURN QUERY SELECT v_badge.id, v_badge.name, v_badge.symbol, TRUE;
          END IF;
          
        WHEN 'topics_mastered' THEN
          IF user_stats.mastered_topics >= v_badge.requirement_value THEN
            INSERT INTO public.user_badges (user_id, badge_id, metadata)
            VALUES (p_user_id, v_badge.id, jsonb_build_object('mastered_topics', user_stats.mastered_topics));
            
            RETURN QUERY SELECT v_badge.id, v_badge.name, v_badge.symbol, TRUE;
          END IF;
          
        WHEN 'topics_completed' THEN
          IF user_stats.completed_topics >= v_badge.requirement_value THEN
            INSERT INTO public.user_badges (user_id, badge_id, metadata)
            VALUES (p_user_id, v_badge.id, jsonb_build_object('completed_topics', user_stats.completed_topics));
            
            RETURN QUERY SELECT v_badge.id, v_badge.name, v_badge.symbol, TRUE;
          END IF;
      END CASE;
    ELSE
      -- Badge already unlocked, return it but mark as not newly unlocked
      RETURN QUERY SELECT v_badge.id, v_badge.name, v_badge.symbol, FALSE;
    END IF;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.check_and_award_badges IS 'Checks user stats and awards eligible badges automatically';

-- =============================================================================
-- TRIGGER: Auto-check badges after XP update
-- =============================================================================
CREATE OR REPLACE FUNCTION public.auto_check_badges()
RETURNS TRIGGER AS $$
BEGIN
  -- Check and award badges for the user
  PERFORM public.check_and_award_badges(NEW.user_id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS on_user_xp_update ON public.users;
CREATE TRIGGER on_user_xp_update
  AFTER UPDATE OF total_xp, level ON public.users
  FOR EACH ROW
  WHEN (OLD.total_xp IS DISTINCT FROM NEW.total_xp OR OLD.level IS DISTINCT FROM NEW.level)
  EXECUTE FUNCTION public.auto_check_badges();

-- =============================================================================
-- SEED DATA: Default Badges
-- =============================================================================
INSERT INTO public.badges (badge_key, name, description, category, requirement_type, requirement_value, symbol, tier)
VALUES
  -- Level-based badges
  ('novice_scholar', 'Novice Scholar', 'Reached Level 5 - Your learning journey begins', 'level', 'level', 5, '[★]', 1),
  ('curious_mind', 'Curious Mind', 'Reached Level 10 - Knowledge is growing', 'level', 'level', 10, '[★★]', 2),
  ('knowledge_seeker', 'Knowledge Seeker', 'Reached Level 20 - Pursuing wisdom relentlessly', 'level', 'level', 20, '[★★★]', 3),
  ('sage', 'Sage', 'Reached Level 30 - Mastery approaches', 'level', 'level', 30, '[★★★★]', 4),
  ('grand_master', 'Grand Master', 'Reached Level 50 - Legendary status achieved', 'level', 'level', 50, '[◆]', 4),
  
  -- XP-based badges
  ('xp_collector', 'XP Collector', 'Earned 1,000 total XP', 'achievement', 'total_xp', 1000, '[●]', 1),
  ('xp_hoarder', 'XP Hoarder', 'Earned 5,000 total XP', 'achievement', 'total_xp', 5000, '[●●]', 2),
  ('xp_master', 'XP Master', 'Earned 10,000 total XP', 'achievement', 'total_xp', 10000, '[●●●]', 3),
  ('xp_legend', 'XP Legend', 'Earned 25,000 total XP', 'achievement', 'total_xp', 25000, '[◆]', 4),
  
  -- Quiz-based badges
  ('first_quiz', 'First Steps', 'Completed your first quiz', 'quiz', 'quizzes_completed', 1, '[✓]', 1),
  ('quiz_enthusiast', 'Quiz Enthusiast', 'Completed 10 quizzes', 'quiz', 'quizzes_completed', 10, '[✓✓]', 1),
  ('quiz_addict', 'Quiz Addict', 'Completed 50 quizzes', 'quiz', 'quizzes_completed', 50, '[✓✓✓]', 2),
  ('quiz_master', 'Quiz Master', 'Completed 100 quizzes', 'quiz', 'quizzes_completed', 100, '[✓✓✓✓]', 3),
  ('quiz_legend', 'Quiz Legend', 'Completed 250 quizzes', 'quiz', 'quizzes_completed', 250, '[◆]', 4),
  
  -- Topic mastery badges
  ('first_mastery', 'First Mastery', 'Mastered your first topic (90%+ score)', 'achievement', 'topics_mastered', 1, '[♦]', 1),
  ('topic_master', 'Topic Master', 'Mastered 5 different topics', 'achievement', 'topics_mastered', 5, '[♦♦]', 2),
  ('subject_expert', 'Subject Expert', 'Mastered 10 different topics', 'achievement', 'topics_mastered', 10, '[♦♦♦]', 3),
  ('polymath', 'Polymath', 'Mastered 20 different topics', 'achievement', 'topics_mastered', 20, '[◆]', 4),
  
  -- Completion badges
  ('topic_explorer', 'Topic Explorer', 'Completed 3 different topics', 'achievement', 'topics_completed', 3, '[▪]', 1),
  ('diverse_learner', 'Diverse Learner', 'Completed 10 different topics', 'achievement', 'topics_completed', 10, '[▪▪]', 2),
  ('knowledge_hoarder', 'Knowledge Hoarder', 'Completed 25 different topics', 'achievement', 'topics_completed', 25, '[▪▪▪]', 3)
ON CONFLICT (badge_key) DO NOTHING;

-- =============================================================================
-- SEED DATA: Milestones
-- =============================================================================
INSERT INTO public.milestones (milestone_key, name, description, category, threshold, symbol)
VALUES
  ('xp_100', '100 XP Milestone', 'Earned your first 100 XP', 'xp', 100, '[!]'),
  ('xp_500', '500 XP Milestone', 'Reached 500 total XP', 'xp', 500, '[!!]'),
  ('xp_1000', '1,000 XP Milestone', 'Hit the 1K XP mark', 'xp', 1000, '[!!!]'),
  ('xp_2500', '2,500 XP Milestone', 'Accumulated 2,500 XP', 'xp', 2500, '[!!!!]'),
  ('xp_5000', '5,000 XP Milestone', 'Reached 5K XP - Impressive!', 'xp', 5000, '[◆]'),
  ('xp_10000', '10,000 XP Milestone', 'Hit the 10K milestone!', 'xp', 10000, '[◆◆]'),
  
  ('quiz_5', '5 Quizzes', 'Completed 5 quizzes', 'quiz', 5, '[►]'),
  ('quiz_25', '25 Quizzes', 'Completed 25 quizzes', 'quiz', 25, '[►►]'),
  ('quiz_100', '100 Quizzes', 'Century of quizzes!', 'quiz', 100, '[►►►]'),
  ('quiz_500', '500 Quizzes', 'Half a thousand quizzes!', 'quiz', 500, '[◆]'),
  
  ('topics_5', '5 Topics', 'Studied 5 different topics', 'topic', 5, '[▼]'),
  ('topics_10', '10 Topics', 'Explored 10 topics', 'topic', 10, '[▼▼]'),
  ('topics_25', '25 Topics', 'Quarter century of topics!', 'topic', 25, '[▼▼▼]')
ON CONFLICT (milestone_key) DO NOTHING;

-- =============================================================================
-- ENABLE REALTIME
-- =============================================================================
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_badges;
ALTER PUBLICATION supabase_realtime ADD TABLE public.user_milestones;

-- =============================================================================
-- UTILITY VIEW: User Achievements Summary
-- =============================================================================
CREATE OR REPLACE VIEW public.user_achievements_summary AS
SELECT 
  u.user_id,
  u.username,
  u.total_xp,
  u.level,
  COUNT(DISTINCT ub.badge_id) as total_badges,
  COUNT(DISTINCT ub.badge_id) FILTER (WHERE b.tier = 1) as bronze_badges,
  COUNT(DISTINCT ub.badge_id) FILTER (WHERE b.tier = 2) as silver_badges,
  COUNT(DISTINCT ub.badge_id) FILTER (WHERE b.tier = 3) as gold_badges,
  COUNT(DISTINCT ub.badge_id) FILTER (WHERE b.tier = 4) as platinum_badges,
  COUNT(DISTINCT um.milestone_id) as total_milestones,
  MAX(ub.unlocked_at) as latest_badge_at
FROM public.users u
LEFT JOIN public.user_badges ub ON ub.user_id = u.user_id
LEFT JOIN public.badges b ON b.id = ub.badge_id
LEFT JOIN public.user_milestones um ON um.user_id = u.user_id
GROUP BY u.user_id, u.username, u.total_xp, u.level;

COMMENT ON VIEW public.user_achievements_summary IS 'Summary of user badges and milestones';

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- Check tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public' 
AND tablename IN ('badges', 'user_badges', 'milestones', 'user_milestones');

-- Check badges
SELECT badge_key, name, requirement_type, requirement_value, symbol, tier 
FROM public.badges 
ORDER BY tier, requirement_value;

-- Check milestones
SELECT milestone_key, name, threshold, symbol 
FROM public.milestones 
ORDER BY threshold;

-- Test badge checking for demo user
SELECT * FROM public.check_and_award_badges('demo_user');

-- View demo user badges
SELECT 
  b.symbol,
  b.name,
  b.description,
  ub.unlocked_at
FROM public.user_badges ub
JOIN public.badges b ON b.id = ub.badge_id
WHERE ub.user_id = 'demo_user'
ORDER BY ub.unlocked_at DESC;

-- =============================================================================
-- MIGRATION COMPLETE! 🎉
-- =============================================================================
-- Created:
--   ✓ badges table (21 default badges)
--   ✓ user_badges table
--   ✓ milestones table (13 default milestones)
--   ✓ user_milestones table
--   ✓ Auto-badge checking function
--   ✓ Trigger to award badges on XP/level change
--   ✓ Achievement summary view
--
-- Features:
--   ✓ Level-based badges (Novice Scholar at L5, etc.)
--   ✓ XP milestones
--   ✓ Quiz completion badges
--   ✓ Topic mastery tracking
--   ✓ 4-tier system (Bronze, Silver, Gold, Platinum)
--   ✓ ASCII symbols for each badge
--   ✓ Real-time updates enabled
--
-- Next: Create FastAPI routes and frontend UI
-- =============================================================================
