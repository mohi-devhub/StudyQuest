"""
Test AI Response Caching
Verifies that the AI cache works correctly
"""
import time
from utils.ai_cache import AIResponseCache


def test_cache_basic_operations():
    """Test basic cache set and get operations"""
    cache = AIResponseCache(ttl_seconds=2)
    
    # Test cache miss
    result = cache.get("test prompt", "test-model")
    assert result is None, "Cache should be empty initially"
    
    # Test cache set and hit
    test_response = {"questions": ["Q1", "Q2"], "metadata": {"test": True}}
    cache.set("test prompt", "test-model", test_response)
    
    cached = cache.get("test prompt", "test-model")
    assert cached is not None, "Cache should return stored value"
    assert cached["questions"] == ["Q1", "Q2"], "Cached data should match"
    assert cached["metadata"]["test"] is True, "Cached metadata should match"
    
    print("✓ Basic cache operations work")


def test_cache_key_generation():
    """Test that cache keys are generated consistently"""
    cache = AIResponseCache()
    
    # Same inputs should generate same key
    key1 = cache.generate_cache_key("prompt", "model", difficulty="medium", num=5)
    key2 = cache.generate_cache_key("prompt", "model", difficulty="medium", num=5)
    assert key1 == key2, "Same inputs should generate same cache key"
    
    # Different inputs should generate different keys
    key3 = cache.generate_cache_key("prompt", "model", difficulty="hard", num=5)
    assert key1 != key3, "Different inputs should generate different cache keys"
    
    # Order of kwargs shouldn't matter
    key4 = cache.generate_cache_key("prompt", "model", num=5, difficulty="medium")
    assert key1 == key4, "Kwargs order shouldn't affect cache key"
    
    print("✓ Cache key generation works correctly")


def test_cache_expiration():
    """Test that cache entries expire after TTL"""
    cache = AIResponseCache(ttl_seconds=1)
    
    # Set a value
    cache.set("test prompt", "test-model", {"data": "test"})
    
    # Should be available immediately
    result = cache.get("test prompt", "test-model")
    assert result is not None, "Cache should return value before expiration"
    
    # Wait for expiration
    time.sleep(1.5)
    
    # Should be expired now
    result = cache.get("test prompt", "test-model")
    assert result is None, "Cache should return None after expiration"
    
    print("✓ Cache expiration works correctly")


def test_cache_with_parameters():
    """Test cache with different parameters"""
    cache = AIResponseCache()
    
    # Store responses with different parameters
    cache.set("notes", "model", {"quiz": "easy"}, difficulty="easy", num=5)
    cache.set("notes", "model", {"quiz": "hard"}, difficulty="hard", num=5)
    
    # Retrieve with correct parameters
    easy_quiz = cache.get("notes", "model", difficulty="easy", num=5)
    hard_quiz = cache.get("notes", "model", difficulty="hard", num=5)
    
    assert easy_quiz["quiz"] == "easy", "Should retrieve easy quiz"
    assert hard_quiz["quiz"] == "hard", "Should retrieve hard quiz"
    
    # Different parameters should not match
    wrong_params = cache.get("notes", "model", difficulty="medium", num=5)
    assert wrong_params is None, "Wrong parameters should not match cache"
    
    print("✓ Cache with parameters works correctly")


def test_cache_stats():
    """Test cache statistics"""
    cache = AIResponseCache()
    
    # Empty cache stats
    stats = cache.get_stats()
    assert stats["total_entries"] == 0, "Empty cache should have 0 entries"
    assert stats["total_hits"] == 0, "Empty cache should have 0 hits"
    
    # Add some entries
    cache.set("prompt1", "model", {"data": 1})
    cache.set("prompt2", "model", {"data": 2})
    
    # Get stats
    stats = cache.get_stats()
    assert stats["total_entries"] == 2, "Cache should have 2 entries"
    
    # Access an entry to increase hits
    cache.get("prompt1", "model")
    cache.get("prompt1", "model")
    
    stats = cache.get_stats()
    assert stats["total_hits"] == 2, "Cache should have 2 hits"
    
    print("✓ Cache statistics work correctly")


def test_cache_invalidation():
    """Test cache invalidation"""
    cache = AIResponseCache()
    
    # Set a value
    cache.set("test prompt", "test-model", {"data": "test"})
    
    # Verify it's cached
    result = cache.get("test prompt", "test-model")
    assert result is not None, "Value should be cached"
    
    # Invalidate
    success = cache.invalidate("test prompt", "test-model")
    assert success is True, "Invalidation should succeed"
    
    # Verify it's gone
    result = cache.get("test prompt", "test-model")
    assert result is None, "Value should be invalidated"
    
    # Invalidate non-existent entry
    success = cache.invalidate("non-existent", "model")
    assert success is False, "Invalidating non-existent entry should return False"
    
    print("✓ Cache invalidation works correctly")


def test_cache_clear():
    """Test clearing entire cache"""
    cache = AIResponseCache()
    
    # Add multiple entries
    cache.set("prompt1", "model", {"data": 1})
    cache.set("prompt2", "model", {"data": 2})
    cache.set("prompt3", "model", {"data": 3})
    
    stats = cache.get_stats()
    assert stats["total_entries"] == 3, "Cache should have 3 entries"
    
    # Clear cache
    cache.clear()
    
    stats = cache.get_stats()
    assert stats["total_entries"] == 0, "Cache should be empty after clear"
    
    print("✓ Cache clear works correctly")


def test_global_cache_instances():
    """Test that global cache instances are accessible"""
    from utils.ai_cache import get_quiz_cache, get_recommendation_cache, get_coach_cache
    
    quiz_cache = get_quiz_cache()
    rec_cache = get_recommendation_cache()
    coach_cache = get_coach_cache()
    
    assert quiz_cache is not None, "Quiz cache should be accessible"
    assert rec_cache is not None, "Recommendation cache should be accessible"
    assert coach_cache is not None, "Coach cache should be accessible"
    
    # Verify they are separate instances
    quiz_cache.set("test", "model", {"type": "quiz"})
    rec_cache.set("test", "model", {"type": "rec"})
    
    quiz_result = quiz_cache.get("test", "model")
    rec_result = rec_cache.get("test", "model")
    
    assert quiz_result["type"] == "quiz", "Quiz cache should have quiz data"
    assert rec_result["type"] == "rec", "Rec cache should have rec data"
    
    print("✓ Global cache instances work correctly")


if __name__ == "__main__":
    print("Testing AI Response Cache...")
    print()
    
    test_cache_basic_operations()
    test_cache_key_generation()
    test_cache_expiration()
    test_cache_with_parameters()
    test_cache_stats()
    test_cache_invalidation()
    test_cache_clear()
    test_global_cache_instances()
    
    print()
    print("✅ All AI cache tests passed!")
