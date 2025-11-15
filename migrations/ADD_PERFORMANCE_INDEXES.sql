-- Performance Optimization: Add indexes for core tables
-- This migration adds indexes to improve query performance for common access patterns

-- Index on user_topics(user_id) for faster user-specific topic lookups
CREATE INDEX IF NOT EXISTS idx_user_topics_user_id 
ON user_topics(user_id);

-- Composite index on quiz_scores(user_id, topic) for user-topic score queries
CREATE INDEX IF NOT EXISTS idx_quiz_scores_user_topic 
ON quiz_scores(user_id, topic);

-- Index on xp_history(user_id, created_at DESC) for user XP history with chronological ordering
CREATE INDEX IF NOT EXISTS idx_xp_history_user_created 
ON xp_history(user_id, created_at DESC);

-- Index on user_badges(user_id, unlocked_at DESC) for user badge queries with chronological ordering
CREATE INDEX IF NOT EXISTS idx_user_badges_user_unlocked 
ON user_badges(user_id, unlocked_at DESC);

-- Note: study_sessions table already has appropriate indexes
-- Verify with: SELECT * FROM pg_indexes WHERE tablename = 'study_sessions';
