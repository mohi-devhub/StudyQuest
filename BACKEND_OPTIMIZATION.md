# Backend Optimization & Error Handling

## Overview

Comprehensive optimization of FastAPI endpoints with improved reliability, caching, input validation, and standardized error responses.

---

## 🎯 Key Improvements

### 1. Input Validation
- ✅ Topic length limit: **50 characters max**
- ✅ Topic must contain alphanumeric characters
- ✅ Number of questions: **1-20 range**
- ✅ Difficulty validation: `easy`, `medium`, `hard`, `expert`
- ✅ Automatic whitespace trimming

### 2. Caching System
- ✅ **Supabase-based cache** for notes and quizzes
- ✅ **24-hour expiration** (configurable)
- ✅ **Cache hit tracking** for analytics
- ✅ **Automatic cleanup** of old entries
- ✅ **5 entries max per topic** to prevent bloat

### 3. Error Handling
- ✅ **Standardized JSON error responses**
- ✅ **Graceful API timeout handling** (20-30 second limits)
- ✅ **Fallback messages** for all failure scenarios
- ✅ **Predictable error codes**: `API_TIMEOUT`, `VALIDATION_ERROR`, `GENERATION_ERROR`

### 4. Performance
- ✅ **Timeout protection** prevents hanging requests
- ✅ **Reduced API calls** via intelligent caching
- ✅ **Generation time tracking** in metadata
- ✅ **Parallel processing** support (batch endpoints)

---

## 📁 New Files

### 1. `/backend/utils/error_handlers.py`
Centralized error handling and validation utilities.

**Functions:**
- `validate_topic(topic, max_length=50)` - Topic validation
- `validate_num_questions(num, min=1, max=20)` - Question count validation
- `validate_difficulty(difficulty)` - Difficulty level validation
- `handle_api_timeout_error(operation)` - Timeout error response
- `handle_generation_error(resource)` - Generation failure response
- `handle_database_error(operation)` - Database error response
- `get_fallback_message(resource_type)` - User-friendly fallback messages

**Models:**
```python
class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None

class SuccessResponse(BaseModel):
    status: str = "success"
    data: Any
    message: Optional[str] = None
```

---

### 2. `/backend/utils/cache_utils.py`
Caching utilities for study content.

**Functions:**
- `get_cached_content(topic, content_type, **kwargs)` - Retrieve cached content
- `set_cached_content(topic, content_type, content, **kwargs)` - Store in cache
- `delete_cache_entry(cache_key)` - Remove cache entry
- `cleanup_old_cache_entries(topic, type)` - Auto-cleanup
- `invalidate_topic_cache(topic)` - Clear all cache for topic
- `get_cache_stats(topic=None)` - Cache analytics

**Configuration:**
```python
CACHE_EXPIRATION_HOURS = 24  # Cache TTL
MAX_CACHE_PER_TOPIC = 5      # Prevents unlimited growth
```

---

### 3. `/MIGRATION_CONTENT_CACHE.sql`
Database migration for cache table.

**Schema:**
```sql
CREATE TABLE public.content_cache (
  id UUID PRIMARY KEY,
  cache_key TEXT UNIQUE NOT NULL,     -- MD5 hash
  topic TEXT NOT NULL,                -- Normalized topic
  content_type TEXT NOT NULL,         -- 'notes', 'quiz', 'study_package'
  content JSONB NOT NULL,             -- Actual cached data
  metadata JSONB DEFAULT '{}',        -- Generation params
  hit_count INTEGER DEFAULT 0,        -- Access counter
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
- `idx_content_cache_topic` - Fast topic lookup
- `idx_content_cache_type` - Filter by content type
- `idx_content_cache_key` - Unique key lookup
- `idx_content_cache_last_accessed` - Cleanup queries

**Functions:**
- `cleanup_expired_cache()` - Removes entries older than 7 days

---

## 🔧 Updated Endpoints

### `/study` (POST)
**Optimizations:**
- ✅ Topic validation (≤ 50 chars)
- ✅ Cache check before generation
- ✅ 30-second timeout protection
- ✅ Generation time tracking
- ✅ Automatic cache storage

**Request:**
```json
{
  "topic": "Python Decorators",
  "num_questions": 5,
  "use_cache": true
}
```

**Success Response:**
```json
{
  "topic": "Python Decorators",
  "notes": {
    "topic": "Python Decorators",
    "summary": "...",
    "key_points": ["..."]
  },
  "quiz": [...],
  "metadata": {
    "num_key_points": 7,
    "num_questions": 5,
    "cached": false,
    "generation_time_ms": 2345
  }
}
```

**Error Response (Timeout):**
```json
{
  "status": "error",
  "message": "Request timeout. The API request took too long. Please try again.",
  "code": "API_TIMEOUT",
  "suggestion": "Please try again in a few moments or choose a different topic."
}
```

**Error Response (Generation Failure):**
```json
{
  "status": "error",
  "message": "Unable to generate complete study package at this time.",
  "code": "GENERATION_ERROR",
  "suggestion": "Please try again later or contact support if the issue persists."
}
```

---

### `/quiz/generate` (POST)
**Optimizations:**
- ✅ Notes length validation
- ✅ 20-second timeout protection
- ✅ Fallback messages on failure

**Error Response:**
```json
{
  "status": "error",
  "message": "Unable to generate quiz questions at this time.",
  "code": "API_TIMEOUT",
  "suggestion": "Please try again in a few moments or choose a different topic."
}
```

---

### `/quiz/generate-from-topic` (POST)
**Optimizations:**
- ✅ Topic validation (≤ 50 chars)
- ✅ Cache support
- ✅ 20-second timeout protection
- ✅ Key points validation

**Request:**
```json
{
  "topic": "Python Functions",
  "summary": "Functions are reusable blocks...",
  "key_points": ["...", "..."],
  "num_questions": 5,
  "use_cache": true
}
```

**Cache Hit Response:**
Same structure, but retrieved instantly from cache.

---

### `/progress/v2/submit-quiz` (POST)
**Optimizations:**
- ✅ Topic validation (≤ 50 chars)
- ✅ Difficulty validation
- ✅ Score validation (correct ≤ total)
- ✅ Graceful database error handling
- ✅ Detailed error messages

**Request:**
```json
{
  "user_id": "demo_user",
  "topic": "Python Basics",
  "difficulty": "medium",
  "correct": 4,
  "total": 5,
  "time_taken": 120
}
```

**Success Response:**
```json
{
  "status": "success",
  "quiz_id": "uuid-here",
  "score": 80.0,
  "correct": 4,
  "total": 5,
  "xp_earned": 130,
  "xp_change": {
    "previous_xp": 1000,
    "new_xp": 1130,
    "previous_level": 3,
    "new_level": 3,
    "leveled_up": false
  },
  "feedback": "Good job! Keep practicing."
}
```

**Error Response (Validation):**
```json
{
  "status": "error",
  "message": "Topic cannot exceed 50 characters",
  "code": "VALIDATION_ERROR"
}
```

**Error Response (Database):**
```json
{
  "status": "error",
  "message": "Database error during quiz submission. Please try again.",
  "code": "DATABASE_ERROR"
}
```

---

## 🚀 Usage Examples

### Example 1: Generate Study Package with Cache
```python
import requests

response = requests.post('http://localhost:8000/study', json={
    "topic": "React Hooks",
    "num_questions": 5,
    "use_cache": True
})

data = response.json()

if "metadata" in data and data["metadata"].get("cached"):
    print("✅ Served from cache!")
    print(f"🚀 Cache hit saved API call")
else:
    print(f"🔧 Generated in {data['metadata']['generation_time_ms']}ms")
```

### Example 2: Handle Timeout Gracefully
```python
try:
    response = requests.post('http://localhost:8000/study', json={
        "topic": "Advanced Quantum Physics",
        "num_questions": 10
    }, timeout=35)
    
    if response.status_code == 504:
        error = response.json()
        print(f"⏱️ Timeout: {error['message']}")
        print(f"💡 Suggestion: {error['suggestion']}")
    
except requests.exceptions.Timeout:
    print("Request timed out on client side")
```

### Example 3: Validate Input Before Sending
```python
def validate_topic(topic: str) -> bool:
    if len(topic) > 50:
        print(f"❌ Topic too long: {len(topic)} chars (max 50)")
        return False
    
    if not any(c.isalnum() for c in topic):
        print("❌ Topic must contain letters or numbers")
        return False
    
    return True

topic = input("Enter topic: ")
if validate_topic(topic):
    # Make API call
    pass
```

---

## 📊 Cache Performance

### Cache Hit Rate
```python
from utils.cache_utils import get_cache_stats

stats = await get_cache_stats()
print(f"Total Entries: {stats['total_entries']}")
print(f"Total Hits: {stats['total_hits']}")
print(f"Avg Hits/Entry: {stats['avg_hits_per_entry']:.2f}")

for content_type, type_stats in stats['by_type'].items():
    print(f"{content_type}: {type_stats['count']} entries, {type_stats['hits']} hits")
```

**Example Output:**
```
Total Entries: 47
Total Hits: 156
Avg Hits/Entry: 3.32

study_package: 15 entries, 89 hits
quiz: 22 entries, 51 hits
notes: 10 entries, 16 hits
```

### Cache Invalidation
```python
from utils.cache_utils import invalidate_topic_cache

# Clear all cache for a topic (e.g., after content update)
await invalidate_topic_cache("Python Basics")
```

---

## ⚙️ Configuration

### Timeout Settings
```python
# /backend/routes/study.py
STUDY_PACKAGE_TIMEOUT = 30.0  # seconds

# /backend/routes/quiz.py
QUIZ_GENERATION_TIMEOUT = 20.0  # seconds
```

### Cache Settings
```python
# /backend/utils/cache_utils.py
CACHE_EXPIRATION_HOURS = 24
MAX_CACHE_PER_TOPIC = 5
```

### Validation Limits
```python
# /backend/utils/error_handlers.py
TOPIC_MAX_LENGTH = 50
MIN_QUESTIONS = 1
MAX_QUESTIONS = 20
```

---

## 🧪 Testing

### Test Input Validation
```bash
# Topic too long
curl -X POST http://localhost:8000/study \
  -H "Content-Type: application/json" \
  -d '{"topic": "This is a very long topic name that exceeds the fifty character limit", "num_questions": 5}'

# Expected: 400 Bad Request
# {"status":"error","message":"Topic cannot exceed 50 characters","code":"VALIDATION_ERROR"}
```

### Test Cache Behavior
```bash
# First request (cold cache)
time curl -X POST http://localhost:8000/study \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Lists", "num_questions": 5, "use_cache": true}'

# Second request (cached)
time curl -X POST http://localhost:8000/study \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Lists", "num_questions": 5, "use_cache": true}'

# Expected: Second request is significantly faster
```

### Test Timeout Handling
```python
import asyncio

async def test_timeout():
    # Simulate slow API
    await asyncio.sleep(40)  # Exceeds 30s timeout
    
# Expected: HTTP 504 with graceful error message
```

---

## 📋 Error Code Reference

| Code | Status | Description | When It Occurs |
|------|--------|-------------|----------------|
| `VALIDATION_ERROR` | 400 | Invalid input parameters | Topic too long, invalid difficulty, etc. |
| `API_TIMEOUT` | 504 | API request timed out | OpenRouter API takes >20-30 seconds |
| `GENERATION_ERROR` | 500 | Content generation failed | AI model error, API unavailable |
| `DATABASE_ERROR` | 500 | Database operation failed | Supabase connection issue |
| `NOT_FOUND` | 404 | Resource not found | User doesn't exist, quiz not found |
| `SUBMISSION_ERROR` | 500 | Quiz submission failed | General submission failure |

---

## 🔄 Migration Steps

### 1. Run Database Migration
```bash
# Copy MIGRATION_CONTENT_CACHE.sql
# Paste into Supabase SQL Editor
# Execute
```

### 2. Verify Migration
```sql
-- Check table created
SELECT tablename FROM pg_tables WHERE tablename = 'content_cache';

-- Check indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'content_cache';

-- View statistics (empty initially)
SELECT * FROM cache_statistics;
```

### 3. Update Backend Code
```bash
cd backend
# Files already updated:
# - routes/study.py
# - routes/quiz.py
# - routes/progress_v2.py
# - utils/error_handlers.py (NEW)
# - utils/cache_utils.py (NEW)
```

### 4. Test Endpoints
```bash
# Start server
cd backend
uvicorn main:app --reload

# Test in another terminal
curl -X POST http://localhost:8000/study \
  -H "Content-Type: application/json" \
  -d '{"topic": "Test Topic", "num_questions": 3, "use_cache": true}'
```

---

## 🎁 Benefits

### For Users
- ✅ **Faster responses** via caching (instant for cached topics)
- ✅ **Clear error messages** that explain what went wrong
- ✅ **Reliable service** with timeout protection
- ✅ **Consistent experience** across all endpoints

### For Developers
- ✅ **Standardized error handling** reduces debugging time
- ✅ **Reusable validation functions** eliminate code duplication
- ✅ **Cache analytics** for performance monitoring
- ✅ **Predictable API responses** easier to integrate

### For Operations
- ✅ **Reduced API costs** (fewer OpenRouter calls)
- ✅ **Better performance** under load
- ✅ **Automatic cache cleanup** prevents database bloat
- ✅ **Error tracking** via standardized codes

---

## 🔮 Future Enhancements

### Planned Features

1. **Redis Integration** (if scaling needed)
   - Faster cache reads/writes
   - Distributed caching
   - TTL at infrastructure level

2. **Cache Warming**
   - Pre-generate common topics
   - Background refresh before expiration

3. **Smart Caching**
   - ML-based cache retention
   - Predictive pre-loading
   - User-specific caching

4. **Advanced Analytics**
   - Cache hit/miss rates by endpoint
   - Generation time trends
   - Error frequency tracking

5. **Rate Limiting**
   - Per-user request limits
   - Graceful degradation
   - Queue system for high load

---

## 📝 Commit Message

```
ops: Optimize FastAPI endpoints and add graceful error handling

Implemented comprehensive backend optimizations for reliability and performance.

New Utilities:
- error_handlers.py
  * Centralized validation functions (topic ≤50 chars, difficulty, num_questions)
  * Standardized error responses (ErrorResponse, SuccessResponse models)
  * Graceful error handlers (timeout, generation, database, not_found)
  * Fallback messages for all failure scenarios
  * Error codes: API_TIMEOUT, VALIDATION_ERROR, GENERATION_ERROR, DATABASE_ERROR

- cache_utils.py
  * Supabase-based content caching (notes, quizzes, study packages)
  * Cache key generation (MD5 hash of topic + params)
  * 24-hour expiration with auto-cleanup
  * Max 5 entries per topic to prevent bloat
  * Hit count tracking for analytics
  * Cache statistics view

Database:
- MIGRATION_CONTENT_CACHE.sql
  * content_cache table with JSONB storage
  * Indexes for performance (topic, type, key, last_accessed)
  * RLS policies (public read/write)
  * cleanup_expired_cache() function (removes >7 days old)
  * cache_statistics view

Updated Endpoints:

/study (POST):
- Input validation (topic ≤ 50 chars, num_questions 1-20)
- Cache check before generation (use_cache parameter)
- 30-second timeout protection
- Generation time tracking in metadata
- Automatic cache storage on success
- Standardized error responses

/quiz/generate (POST):
- Notes validation
- 20-second timeout protection
- Graceful error messages
- Fallback suggestions

/quiz/generate-from-topic (POST):
- Topic validation (≤ 50 chars)
- Cache support (use_cache parameter)
- 20-second timeout protection
- Key points validation
- Automatic cache storage

/progress/v2/submit-quiz (POST):
- Topic validation (≤ 50 chars)
- Difficulty validation (easy/medium/hard/expert)
- Score validation (correct ≤ total)
- Graceful database error handling
- Detailed error messages with codes
- Continue-on-error for non-critical operations

Features:
- ✓ Input validation (topic ≤ 50 chars everywhere)
- ✓ Timeout protection (20-30s limits)
- ✓ Caching to reduce API calls
- ✓ Standardized JSON error responses
- ✓ Predictable error codes
- ✓ Fallback messages
- ✓ Generation time tracking
- ✓ Cache hit analytics
- ✓ Automatic cache cleanup

Performance Improvements:
- Reduced OpenRouter API calls via intelligent caching
- Instant responses for cached content
- Timeout protection prevents hanging requests
- Database error resilience
- Cache statistics for monitoring

Error Handling:
- API_TIMEOUT: 504 status with retry suggestions
- VALIDATION_ERROR: 400 status with specific field errors
- GENERATION_ERROR: 500 status with fallback messages
- DATABASE_ERROR: 500 status for Supabase issues
- NOT_FOUND: 404 status for missing resources

Cache Performance:
- 24-hour TTL (configurable)
- Max 5 entries per topic
- Automatic cleanup of >7 day old entries
- Hit count tracking
- Cache statistics by content type

Documentation:
- Created BACKEND_OPTIMIZATION.md
  * Detailed feature explanations
  * API examples with error responses
  * Cache performance monitoring
  * Testing procedures
  * Configuration options
  * Migration steps
  * Error code reference
```

---

## 📚 Additional Resources

- [FastAPI Error Handling Best Practices](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [Supabase JSONB Performance](https://supabase.com/docs/guides/database/json)
- [Input Validation with Pydantic](https://docs.pydantic.dev/latest/concepts/validators/)

---

**Version:** 1.1.0  
**Date:** November 6, 2025  
**Status:** ✅ Implemented and Tested
