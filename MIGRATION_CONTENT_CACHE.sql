-- ===========================================================================
-- MIGRATION: Content Cache System
-- ===========================================================================
-- This migration adds a cache table for storing generated study notes and quizzes
-- to reduce API calls and improve performance
-- Run this in Supabase SQL Editor
-- ===========================================================================

-- =============================================================================
-- TABLE: content_cache
-- =============================================================================
CREATE TABLE IF NOT EXISTS public.content_cache (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  cache_key TEXT NOT NULL UNIQUE,
  topic TEXT NOT NULL,
  content_type TEXT NOT NULL,  -- 'notes', 'quiz', 'study_package'
  content JSONB NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  hit_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE public.content_cache IS 'Caches generated study notes and quizzes to reduce API calls';
COMMENT ON COLUMN public.content_cache.cache_key IS 'MD5 hash of topic + type + params';
COMMENT ON COLUMN public.content_cache.topic IS 'Topic name (normalized)';
COMMENT ON COLUMN public.content_cache.content_type IS 'Type of cached content: notes, quiz, or study_package';
COMMENT ON COLUMN public.content_cache.content IS 'The actual cached content (notes, questions, etc.)';
COMMENT ON COLUMN public.content_cache.metadata IS 'Additional parameters used in generation (num_questions, etc.)';
COMMENT ON COLUMN public.content_cache.hit_count IS 'Number of times this cache entry was accessed';
COMMENT ON COLUMN public.content_cache.created_at IS 'When the cache entry was created';
COMMENT ON COLUMN public.content_cache.last_accessed_at IS 'Last time this cache was accessed';

-- =============================================================================
-- INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_content_cache_topic ON public.content_cache(topic);
CREATE INDEX IF NOT EXISTS idx_content_cache_type ON public.content_cache(content_type);
CREATE INDEX IF NOT EXISTS idx_content_cache_key ON public.content_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_content_cache_last_accessed ON public.content_cache(last_accessed_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_cache_created ON public.content_cache(created_at DESC);

-- =============================================================================
-- RLS POLICIES
-- =============================================================================
ALTER TABLE public.content_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Cache entries are viewable by everyone"
  ON public.content_cache FOR SELECT USING (true);

CREATE POLICY "Cache entries can be inserted by everyone"
  ON public.content_cache FOR INSERT WITH CHECK (true);

CREATE POLICY "Cache entries can be updated by everyone"
  ON public.content_cache FOR UPDATE USING (true);

CREATE POLICY "Cache entries can be deleted by everyone"
  ON public.content_cache FOR DELETE USING (true);

-- =============================================================================
-- CLEANUP FUNCTION
-- =============================================================================
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS INTEGER AS $$
DECLARE
  deleted_count INTEGER;
BEGIN
  -- Delete cache entries older than 7 days
  DELETE FROM public.content_cache
  WHERE created_at < NOW() - INTERVAL '7 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  RAISE NOTICE 'Cleaned up % expired cache entries', deleted_count;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cleanup_expired_cache IS 'Removes cache entries older than 7 days';

-- =============================================================================
-- CACHE STATISTICS VIEW
-- =============================================================================
CREATE OR REPLACE VIEW public.cache_statistics AS
SELECT 
  content_type,
  COUNT(*) as total_entries,
  SUM(hit_count) as total_hits,
  ROUND(AVG(hit_count), 2) as avg_hits_per_entry,
  MAX(hit_count) as max_hits,
  COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '24 hours') as entries_last_24h,
  SUM(hit_count) FILTER (WHERE last_accessed_at > NOW() - INTERVAL '24 hours') as hits_last_24h
FROM public.content_cache
GROUP BY content_type;

COMMENT ON VIEW public.cache_statistics IS 'Cache performance statistics by content type';

-- =============================================================================
-- OPTIONAL: AUTOMATIC CLEANUP (Requires pg_cron extension)
-- =============================================================================
-- Uncomment below if you have pg_cron extension enabled
-- This will run cleanup daily at 2 AM

-- SELECT cron.schedule(
--   'cleanup-content-cache',
--   '0 2 * * *',
--   'SELECT cleanup_expired_cache()'
-- );

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Check table exists
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'content_cache';

-- Check indexes
SELECT indexname FROM pg_indexes WHERE schemaname = 'public' AND tablename = 'content_cache';

-- View cache statistics (will be empty initially)
SELECT * FROM public.cache_statistics;

-- =============================================================================
-- SAMPLE USAGE
-- =============================================================================

-- Insert a sample cache entry
INSERT INTO public.content_cache (
  cache_key,
  topic,
  content_type,
  content,
  metadata
) VALUES (
  '123abc',
  'Python Basics',
  'study_package',
  '{"notes": {"summary": "..."}, "quiz": [...]}'::jsonb,
  '{"num_questions": 5}'::jsonb
);

-- Query cache entries
SELECT cache_key, topic, content_type, hit_count, created_at 
FROM public.content_cache 
ORDER BY last_accessed_at DESC 
LIMIT 10;

-- Manual cleanup test
SELECT cleanup_expired_cache();

-- =============================================================================
-- ROLLBACK (if needed)
-- =============================================================================

-- DROP VIEW IF EXISTS public.cache_statistics;
-- DROP FUNCTION IF EXISTS cleanup_expired_cache();
-- DROP TABLE IF EXISTS public.content_cache CASCADE;

-- =============================================================================
-- MIGRATION COMPLETE! ✅
-- =============================================================================
