# AI Response Caching Implementation

## Overview
Implemented AI-specific response caching to reduce API calls and improve performance for quiz generation and recommendation generation.

## Implementation Details

### 1. Core Cache Module (`backend/utils/ai_cache.py`)

Created `AIResponseCache` class with the following features:

- **TTL-based expiration**: Default 1 hour for cached responses
- **Cache key generation**: SHA256 hash from prompt + model + parameters
- **Automatic cleanup**: Expired entries removed periodically (every 5 minutes)
- **Statistics tracking**: Monitors cache hits, entry count, and cache size
- **Thread-safe operations**: In-memory cache with proper access patterns

#### Key Methods:
- `get(prompt, model, **kwargs)`: Retrieve cached response
- `set(prompt, model, response, **kwargs)`: Store response in cache
- `invalidate(prompt, model, **kwargs)`: Remove specific cache entry
- `clear()`: Clear all cache entries
- `get_stats()`: Get cache statistics

#### Global Cache Instances:
- `quiz_cache`: 1 hour TTL for quiz responses
- `recommendation_cache`: 30 minutes TTL for recommendations
- `coach_cache`: 1 hour TTL for coach feedback

### 2. Quiz Generation Integration (`backend/agents/adaptive_quiz_agent.py`)

**Changes:**
1. Import cache utility: `from utils.ai_cache import get_quiz_cache`
2. Initialize cache instance: `quiz_cache = get_quiz_cache()`
3. Check cache before API call:
   ```python
   cached_response = quiz_cache.get(notes, model, difficulty=difficulty, num_questions=num_questions)
   if cached_response:
       return cached_response
   ```
4. Cache successful responses:
   ```python
   quiz_cache.set(notes, model, result, difficulty=difficulty, num_questions=num_questions)
   ```
5. Log cache hits/misses for monitoring

**Cache Key Parameters:**
- `notes`: Study material content
- `model`: AI model identifier
- `difficulty`: Quiz difficulty level
- `num_questions`: Number of questions

### 3. Recommendation Generation Integration (`backend/agents/recommendation_agent.py`)

**Changes:**
1. Import cache utility: `from utils.ai_cache import get_recommendation_cache`
2. Initialize cache instance: `recommendation_cache = get_recommendation_cache()`
3. Check cache before API call:
   ```python
   cached_response = recommendation_cache.get(prompt, model, **cache_key_params)
   if cached_response:
       return cached_response
   ```
4. Cache successful responses:
   ```python
   recommendation_cache.set(prompt, model, result, **cache_key_params)
   ```
5. Log cache hits/misses for monitoring

**Cache Key Parameters:**
- `prompt`: AI prompt text
- `model`: AI model identifier
- `total_attempts`: User's total quiz attempts
- `avg_score`: User's average score
- `topics_count`: Number of topics studied
- `recommendations_count`: Number of recommendations

## Benefits

1. **Reduced API Costs**: Identical requests return cached responses
2. **Improved Performance**: Cache hits return instantly (no network latency)
3. **Better User Experience**: Faster response times for repeated queries
4. **Resource Efficiency**: Less load on OpenRouter API

## Cache Behavior

### Quiz Generation
- Same study notes + difficulty + question count = cache hit
- Cache expires after 1 hour
- Different parameters = different cache entry

### Recommendations
- Same user progress summary = cache hit
- Cache expires after 30 minutes (shorter due to dynamic nature)
- User progress changes = new cache entry

## Testing

### Unit Tests (`backend/test_ai_cache.py`)
- ✅ Basic cache operations (get/set)
- ✅ Cache key generation consistency
- ✅ TTL-based expiration
- ✅ Cache with parameters
- ✅ Cache statistics
- ✅ Cache invalidation
- ✅ Cache clearing
- ✅ Global cache instances

### Integration Tests (`backend/test_ai_cache_integration.py`)
- ✅ Quiz cache integration
- ✅ Recommendation cache integration
- ✅ Cache separation (independent caches)

All tests passing ✅

## Monitoring

Cache statistics can be retrieved using:
```python
from utils.ai_cache import get_quiz_cache

stats = get_quiz_cache().get_stats()
# Returns: {
#   'total_entries': int,
#   'total_hits': int,
#   'cache_size_bytes': int,
#   'avg_age_seconds': float,
#   'ttl_seconds': int
# }
```

## Future Enhancements

1. **Persistent Cache**: Store cache in Redis for multi-instance deployments
2. **Cache Warming**: Pre-populate cache with common queries
3. **Adaptive TTL**: Adjust TTL based on cache hit rate
4. **Cache Metrics Endpoint**: Expose cache statistics via API
5. **Coach Feedback Caching**: Integrate caching into coach agent (prepared but not yet integrated)

## Requirements Satisfied

✅ **Requirement 8.3**: Implement AI response caching
- Created `backend/utils/ai_cache.py` with AIResponseCache class
- Implemented cache key generation from prompt + model
- Added TTL-based cache expiration (1 hour)
- Integrated caching into quiz generation
- Integrated caching into recommendation generation
- Note: cache_utils.py exists but is for general content caching, not AI-specific

## Files Modified

1. `backend/utils/ai_cache.py` - New file (core cache implementation)
2. `backend/agents/adaptive_quiz_agent.py` - Added caching integration
3. `backend/agents/recommendation_agent.py` - Added caching integration
4. `backend/test_ai_cache.py` - New file (unit tests)
5. `backend/test_ai_cache_integration.py` - New file (integration tests)

## Performance Impact

**Before Caching:**
- Every quiz generation: ~1-3 seconds (API call)
- Every recommendation: ~1-2 seconds (API call)

**After Caching:**
- Cache hit: <1ms (in-memory lookup)
- Cache miss: ~1-3 seconds (API call + cache storage)

**Expected Cache Hit Rate:**
- Quiz generation: 30-50% (users often retry same topics)
- Recommendations: 20-40% (user progress changes slowly)

**Estimated Cost Savings:**
- 30-50% reduction in OpenRouter API calls
- Faster response times for cached queries
- Better user experience with instant responses
