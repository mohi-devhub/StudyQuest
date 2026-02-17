"""
AI Response Caching Utility
Caches AI-generated responses to reduce API calls and improve performance
"""
import hashlib
import json
import threading
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class AIResponseCache:
    """
    In-memory cache for AI responses with TTL-based expiration.

    This cache is specifically designed for AI-generated content like:
    - Quiz questions
    - Study recommendations
    - Coach feedback

    Features:
    - TTL-based expiration (default: 1 hour)
    - Cache key generation from prompt + model
    - Automatic cleanup of expired entries
    - Thread-safe operations via threading.Lock
    - Max size with LRU eviction to prevent unbounded growth
    """

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 1000):
        """
        Initialize AI response cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds (default: 1 hour)
            max_size: Maximum number of cache entries (default: 1000)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
        self.max_size = max_size
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # Cleanup every 5 minutes
    
    def generate_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """
        Generate a unique cache key from prompt, model, and parameters.
        
        Args:
            prompt: The AI prompt text
            model: The AI model identifier
            **kwargs: Additional parameters (difficulty, num_questions, etc.)
            
        Returns:
            SHA256 hash as cache key
        """
        # Normalize prompt (remove extra whitespace)
        normalized_prompt = " ".join(prompt.split())
        
        # Create key components
        key_parts = [model, normalized_prompt]
        
        # Add sorted kwargs for consistency
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        
        # Generate hash
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get(self, prompt: str, model: str, **kwargs) -> Optional[Dict]:
        """
        Retrieve cached AI response.

        Args:
            prompt: The AI prompt text
            model: The AI model identifier
            **kwargs: Additional parameters used in cache key

        Returns:
            Cached response dict or None if not found/expired
        """
        # Periodic cleanup
        self._cleanup_expired()

        cache_key = self.generate_cache_key(prompt, model, **kwargs)

        with self._lock:
            if cache_key not in self.cache:
                return None

            entry = self.cache[cache_key]

            # Check if expired
            if time.time() - entry['timestamp'] > self.ttl:
                # Remove expired entry
                del self.cache[cache_key]
                return None

            # Update access stats
            entry['hits'] += 1
            entry['last_accessed'] = time.time()

            return entry['response']

    def set(self, prompt: str, model: str, response: Dict, **kwargs) -> None:
        """
        Store AI response in cache.

        Args:
            prompt: The AI prompt text
            model: The AI model identifier
            response: The AI response to cache
            **kwargs: Additional parameters used in cache key
        """
        cache_key = self.generate_cache_key(prompt, model, **kwargs)

        with self._lock:
            # Evict least-recently-accessed entries if at max capacity
            if cache_key not in self.cache and len(self.cache) >= self.max_size:
                self._evict_lru()

            self.cache[cache_key] = {
                'response': response,
                'timestamp': time.time(),
                'last_accessed': time.time(),
                'hits': 0,
                'model': model,
                'metadata': kwargs
            }
    
    def invalidate(self, prompt: str, model: str, **kwargs) -> bool:
        """
        Invalidate a specific cache entry.

        Args:
            prompt: The AI prompt text
            model: The AI model identifier
            **kwargs: Additional parameters used in cache key

        Returns:
            True if entry was found and removed, False otherwise
        """
        cache_key = self.generate_cache_key(prompt, model, **kwargs)

        with self._lock:
            if cache_key in self.cache:
                del self.cache[cache_key]
                return True

        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self.cache.clear()

    def _evict_lru(self) -> None:
        """Evict the least-recently-accessed entry. Must be called with lock held."""
        if not self.cache:
            return
        lru_key = min(self.cache, key=lambda k: self.cache[k]['last_accessed'])
        del self.cache[lru_key]

    def _cleanup_expired(self) -> None:
        """Remove expired cache entries (called periodically)."""
        current_time = time.time()

        # Only cleanup if interval has passed
        if current_time - self._last_cleanup < self._cleanup_interval:
            return

        with self._lock:
            # Find and remove expired entries
            expired_keys = [
                key for key, entry in self.cache.items()
                if current_time - entry['timestamp'] > self.ttl
            ]

            for key in expired_keys:
                del self.cache[key]

            self._last_cleanup = current_time
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            if not self.cache:
                return {
                    'total_entries': 0,
                    'total_hits': 0,
                    'cache_size_bytes': 0,
                    'avg_age_seconds': 0
                }

            current_time = time.time()
            total_hits = sum(entry['hits'] for entry in self.cache.values())
            total_age = sum(current_time - entry['timestamp'] for entry in self.cache.values())

            # Estimate cache size
            cache_size = len(json.dumps(self.cache).encode())

            return {
                'total_entries': len(self.cache),
                'total_hits': total_hits,
                'cache_size_bytes': cache_size,
                'avg_age_seconds': total_age / len(self.cache) if self.cache else 0,
                'ttl_seconds': self.ttl,
                'max_size': self.max_size
            }
    
    def get_entry_info(self, prompt: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific cache entry.

        Args:
            prompt: The AI prompt text
            model: The AI model identifier
            **kwargs: Additional parameters used in cache key

        Returns:
            Entry metadata or None if not found
        """
        cache_key = self.generate_cache_key(prompt, model, **kwargs)

        with self._lock:
            if cache_key not in self.cache:
                return None

            entry = self.cache[cache_key]
            current_time = time.time()

            return {
                'cache_key': cache_key,
                'model': entry['model'],
                'age_seconds': current_time - entry['timestamp'],
                'hits': entry['hits'],
                'expires_in_seconds': self.ttl - (current_time - entry['timestamp']),
                'metadata': entry['metadata']
            }


# Global cache instances for different AI operations
# Using separate caches allows different TTL settings if needed

quiz_cache = AIResponseCache(ttl_seconds=3600)  # 1 hour for quizzes
recommendation_cache = AIResponseCache(ttl_seconds=1800)  # 30 minutes for recommendations
coach_cache = AIResponseCache(ttl_seconds=3600)  # 1 hour for coach feedback


def get_quiz_cache() -> AIResponseCache:
    """Get the global quiz cache instance."""
    return quiz_cache


def get_recommendation_cache() -> AIResponseCache:
    """Get the global recommendation cache instance."""
    return recommendation_cache


def get_coach_cache() -> AIResponseCache:
    """Get the global coach feedback cache instance."""
    return coach_cache
