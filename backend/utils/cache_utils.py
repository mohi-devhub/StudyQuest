"""
Caching Utilities for Study Notes and Quizzes
Reduces API calls by storing generated content in Supabase
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from config.supabase_client import supabase
import json
import hashlib


# ============================================================================
# CACHE CONFIGURATION
# ============================================================================

# Cache expiration time (in hours)
CACHE_EXPIRATION_HOURS = 24

# Maximum cache entries per topic
MAX_CACHE_PER_TOPIC = 5


# ============================================================================
# CACHE KEY GENERATION
# ============================================================================

def generate_cache_key(topic: str, content_type: str, **kwargs) -> str:
    """
    Generate a unique cache key for content.
    
    Args:
        topic: Topic name
        content_type: 'notes', 'quiz', or 'study_package'
        **kwargs: Additional parameters (num_questions, difficulty, etc.)
        
    Returns:
        MD5 hash as cache key
    """
    # Normalize topic
    topic_normalized = topic.strip().lower()
    
    # Create key string
    key_parts = [topic_normalized, content_type]
    
    # Add sorted kwargs
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    key_string = "|".join(key_parts)
    
    # Generate MD5 hash
    return hashlib.md5(key_string.encode()).hexdigest()


# ============================================================================
# CACHE OPERATIONS
# ============================================================================

async def get_cached_content(
    topic: str,
    content_type: str,
    **kwargs
) -> Optional[Dict]:
    """
    Retrieve cached content from Supabase.
    
    Args:
        topic: Topic name
        content_type: 'notes', 'quiz', or 'study_package'
        **kwargs: Additional parameters for cache key
        
    Returns:
        Cached content dict or None if not found/expired
    """
    try:
        cache_key = generate_cache_key(topic, content_type, **kwargs)
        
        # Query cache table
        result = supabase.table('content_cache').select('*').eq(
            'cache_key', cache_key
        ).single().execute()
        
        if not result.data:
            return None
        
        cache_entry = result.data
        
        # Check expiration
        cached_at = datetime.fromisoformat(cache_entry['created_at'].replace('Z', '+00:00'))
        expiration_time = cached_at + timedelta(hours=CACHE_EXPIRATION_HOURS)
        
        if datetime.now(cached_at.tzinfo) > expiration_time:
            # Cache expired, delete it
            await delete_cache_entry(cache_key)
            return None
        
        # Update hit count
        supabase.table('content_cache').update({
            'hit_count': cache_entry['hit_count'] + 1,
            'last_accessed_at': datetime.utcnow().isoformat()
        }).eq('cache_key', cache_key).execute()
        
        return cache_entry['content']
        
    except Exception as e:
        print(f"Cache retrieval error: {str(e)}")
        return None


async def set_cached_content(
    topic: str,
    content_type: str,
    content: Dict,
    **kwargs
) -> bool:
    """
    Store content in cache.
    
    Args:
        topic: Topic name
        content_type: 'notes', 'quiz', or 'study_package'
        content: Content to cache
        **kwargs: Additional parameters for cache key
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cache_key = generate_cache_key(topic, content_type, **kwargs)
        
        # Prepare cache entry
        cache_entry = {
            'cache_key': cache_key,
            'topic': topic.strip(),
            'content_type': content_type,
            'content': content,
            'metadata': kwargs,
            'hit_count': 0,
            'created_at': datetime.utcnow().isoformat(),
            'last_accessed_at': datetime.utcnow().isoformat()
        }
        
        # Upsert cache entry
        supabase.table('content_cache').upsert(cache_entry).execute()
        
        # Clean up old entries for this topic
        await cleanup_old_cache_entries(topic, content_type)
        
        return True
        
    except Exception as e:
        print(f"Cache storage error: {str(e)}")
        return False


async def delete_cache_entry(cache_key: str) -> bool:
    """Delete a specific cache entry"""
    try:
        supabase.table('content_cache').delete().eq('cache_key', cache_key).execute()
        return True
    except Exception as e:
        print(f"Cache deletion error: {str(e)}")
        return False


async def cleanup_old_cache_entries(topic: str, content_type: str) -> None:
    """
    Remove old cache entries if exceeding MAX_CACHE_PER_TOPIC.
    Keeps the most recently accessed entries.
    """
    try:
        # Get all entries for this topic and type
        result = supabase.table('content_cache').select('cache_key, last_accessed_at').eq(
            'topic', topic.strip()
        ).eq('content_type', content_type).order(
            'last_accessed_at', desc=True
        ).execute()
        
        entries = result.data or []
        
        # If we have too many, delete the oldest ones
        if len(entries) > MAX_CACHE_PER_TOPIC:
            to_delete = entries[MAX_CACHE_PER_TOPIC:]
            for entry in to_delete:
                await delete_cache_entry(entry['cache_key'])
                
    except Exception as e:
        print(f"Cache cleanup error: {str(e)}")


async def invalidate_topic_cache(topic: str) -> bool:
    """
    Invalidate all cache entries for a topic.
    Useful when topic content needs to be refreshed.
    """
    try:
        supabase.table('content_cache').delete().eq('topic', topic.strip()).execute()
        return True
    except Exception as e:
        print(f"Cache invalidation error: {str(e)}")
        return False


# ============================================================================
# CACHE STATISTICS
# ============================================================================

async def get_cache_stats(topic: Optional[str] = None) -> Dict:
    """
    Get cache statistics.
    
    Args:
        topic: Optional topic to filter by
        
    Returns:
        Dict with cache statistics
    """
    try:
        query = supabase.table('content_cache').select('*')
        
        if topic:
            query = query.eq('topic', topic.strip())
        
        result = query.execute()
        entries = result.data or []
        
        if not entries:
            return {
                'total_entries': 0,
                'total_hits': 0,
                'avg_hits_per_entry': 0,
                'by_type': {}
            }
        
        # Calculate stats
        total_hits = sum(e['hit_count'] for e in entries)
        by_type = {}
        
        for entry in entries:
            content_type = entry['content_type']
            if content_type not in by_type:
                by_type[content_type] = {'count': 0, 'hits': 0}
            by_type[content_type]['count'] += 1
            by_type[content_type]['hits'] += entry['hit_count']
        
        return {
            'total_entries': len(entries),
            'total_hits': total_hits,
            'avg_hits_per_entry': total_hits / len(entries) if entries else 0,
            'by_type': by_type
        }
        
    except Exception as e:
        print(f"Cache stats error: {str(e)}")
        return {
            'total_entries': 0,
            'total_hits': 0,
            'avg_hits_per_entry': 0,
            'by_type': {},
            'error': str(e)
        }


# ============================================================================
# MIGRATION SQL (Run this in Supabase SQL Editor)
# ============================================================================

CACHE_TABLE_MIGRATION = """
-- Create content_cache table for storing generated content
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

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_content_cache_topic ON public.content_cache(topic);
CREATE INDEX IF NOT EXISTS idx_content_cache_type ON public.content_cache(content_type);
CREATE INDEX IF NOT EXISTS idx_content_cache_key ON public.content_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_content_cache_last_accessed ON public.content_cache(last_accessed_at DESC);

-- RLS Policies
ALTER TABLE public.content_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Cache entries are viewable by everyone"
  ON public.content_cache FOR SELECT USING (true);

CREATE POLICY "Cache entries can be inserted by everyone"
  ON public.content_cache FOR INSERT WITH CHECK (true);

CREATE POLICY "Cache entries can be updated by everyone"
  ON public.content_cache FOR UPDATE USING (true);

CREATE POLICY "Cache entries can be deleted by everyone"
  ON public.content_cache FOR DELETE USING (true);

-- Automatic cleanup of old cache entries (older than 7 days)
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
  DELETE FROM public.content_cache
  WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Optional: Schedule cleanup (requires pg_cron extension)
-- SELECT cron.schedule('cleanup-cache', '0 2 * * *', 'SELECT cleanup_expired_cache()');

COMMENT ON TABLE public.content_cache IS 'Caches generated study notes and quizzes to reduce API calls';
COMMENT ON COLUMN public.content_cache.cache_key IS 'MD5 hash of topic + type + params';
COMMENT ON COLUMN public.content_cache.hit_count IS 'Number of times this cache entry was accessed';
"""
