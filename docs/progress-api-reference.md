# Progress API Reference

Complete API reference for the StudyQuest progress tracking endpoints.

## Base URL

```
http://localhost:8000/progress
```

## Authentication

All endpoints require JWT authentication via Bearer token:

```
Authorization: Bearer <your_jwt_token>
```

Get token from `/auth/login` endpoint.

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/progress/{user_id}` | GET | Fetch complete user progress and XP data |
| `/progress/update` | POST | Update XP after quiz completion or activity |
| `/progress/reset` | POST | Reset progress for a specific topic |
| `/progress/evaluate` | POST | Evaluate quiz and auto-update progress |
| `/progress/stats` | GET | Get aggregated progress statistics |
| `/progress/topics` | GET | Get progress for all topics |
| `/progress/topics/{topic}` | GET | Get progress for specific topic |
| `/progress/xp` | GET | Get total XP and activity stats |
| `/progress/xp/logs` | GET | Get XP earning history |

---

## GET /progress/{user_id}

Fetch comprehensive user data including progress, XP, and recent activity.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `user_id` | UUID | Yes | User's unique identifier |

### Security

- Users can **only** access their own data
- Attempting to access another user's data returns `403 Forbidden`
- The `user_id` must match the authenticated user's ID

### Response

**Success (200 OK)**

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "statistics": {
    "total_topics": 5,
    "completed_topics": 2,
    "in_progress_topics": 3,
    "average_score": 78.5,
    "completion_rate": 40.0
  },
  "topics": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "topic": "Neural Networks",
      "completion_status": "completed",
      "last_attempt": "2025-11-05T10:30:00.000Z",
      "avg_score": 85.50,
      "total_attempts": 2,
      "created_at": "2025-11-04T09:00:00.000Z",
      "updated_at": "2025-11-05T10:30:00.000Z"
    },
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "topic": "Machine Learning",
      "completion_status": "in_progress",
      "last_attempt": "2025-11-05T09:15:00.000Z",
      "avg_score": 65.00,
      "total_attempts": 1,
      "created_at": "2025-11-05T08:30:00.000Z",
      "updated_at": "2025-11-05T09:15:00.000Z"
    }
  ],
  "xp": {
    "total_xp": 450,
    "total_activities": 5,
    "last_activity": "2025-11-05T10:30:00.000Z"
  },
  "recent_xp_logs": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "points": 100,
      "reason": "quiz_completed",
      "metadata": {
        "topic": "Neural Networks",
        "score": 85.0,
        "total_questions": 5,
        "correct_answers": 4
      },
      "timestamp": "2025-11-05T10:30:00.000Z"
    }
  ]
}
```

**Error Responses**

| Status | Description | Response |
|--------|-------------|----------|
| 403 | Forbidden - Accessing another user's data | `{"detail": "Forbidden: You can only access your own progress data"}` |
| 401 | Unauthorized - Invalid/missing token | `{"detail": "Not authenticated"}` |
| 500 | Server error | `{"detail": "Failed to fetch user progress: <error>"}` |

### Example Usage

```bash
# cURL
curl -X GET "http://localhost:8000/progress/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/progress/550e8400-e29b-41d4-a716-446655440000",
        headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()
    print(f"Total XP: {data['xp']['total_xp']}")

# JavaScript (fetch)
const response = await fetch(
  'http://localhost:8000/progress/550e8400-e29b-41d4-a716-446655440000',
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
const data = await response.json();
console.log(`Total XP: ${data.xp.total_xp}`);
```

---

## POST /progress/update

Manually award XP points for various activities.

### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `points` | integer | Yes | 1 ≤ points ≤ 1000 | XP points to award |
| `reason` | string | Yes | 1-100 chars | Activity type/reason |
| `metadata` | object | No | Any valid JSON | Additional context |

### Request Example

```json
{
  "points": 100,
  "reason": "quiz_completed",
  "metadata": {
    "topic": "Neural Networks",
    "score": 85.0,
    "total_questions": 5,
    "correct_answers": 4
  }
}
```

### Common Reasons

| Reason | Typical Points | Use Case |
|--------|----------------|----------|
| `quiz_completed` | 100 | Base points for quiz completion |
| `perfect_score` | 50 | Bonus for 100% quiz score |
| `study_session` | 50 | Completing a study session |
| `daily_streak` | 25 | Daily engagement bonus |
| `achievement_unlocked` | 50-200 | Unlocking achievements |
| `first_topic` | 150 | First topic studied |
| `topic_completed` | 200 | Mastering a topic (70%+ avg) |

### Response

**Success (200 OK)**

```json
{
  "success": true,
  "xp_log": {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "points": 100,
    "reason": "quiz_completed",
    "metadata": {
      "topic": "Neural Networks",
      "score": 85.0
    },
    "timestamp": "2025-11-05T10:30:00.000Z"
  },
  "total_xp": 550,
  "message": "Successfully awarded 100 XP for quiz_completed"
}
```

**Error Responses**

| Status | Description | Example |
|--------|-------------|---------|
| 422 | Validation error | Points out of range (1-1000) |
| 401 | Unauthorized | Invalid/missing token |
| 500 | Server error | Database error |

### Example Usage

```bash
# cURL
curl -X POST "http://localhost:8000/progress/update" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "points": 50,
    "reason": "daily_streak",
    "metadata": {"streak_days": 7}
  }'

# Python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/progress/update",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "points": 50,
            "reason": "daily_streak",
            "metadata": {"streak_days": 7}
        }
    )
    data = response.json()
    print(f"New total XP: {data['total_xp']}")

# JavaScript (fetch)
const response = await fetch('http://localhost:8000/progress/update', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    points: 50,
    reason: 'daily_streak',
    metadata: { streak_days: 7 }
  })
});
const data = await response.json();
console.log(`Awarded: ${data.xp_log.points} XP`);
```

---

## POST /progress/reset

Reset progress for a specific topic, allowing users to start over.

### Request Body

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `topic` | string | Yes | 1-200 chars | Topic name to reset |

### Request Example

```json
{
  "topic": "Neural Networks"
}
```

### Response

**Success (200 OK)**

```json
{
  "success": true,
  "topic": "Neural Networks",
  "message": "Successfully reset progress for topic: Neural Networks",
  "note": "XP earned from this topic has been preserved"
}
```

**Error Responses**

| Status | Description | Response |
|--------|-------------|----------|
| 404 | Topic not found | `{"detail": "No progress found for topic: Neural Networks"}` |
| 422 | Validation error | Empty topic name |
| 401 | Unauthorized | Invalid/missing token |
| 500 | Server error | Database error |

### Behavior

1. **Deletes** the progress record from the database
2. **Preserves** all XP logs (earned XP is NOT removed)
3. User can re-study the topic from scratch
4. Quiz attempts counter resets to 0
5. Average score resets when retaken

### Example Usage

```bash
# cURL
curl -X POST "http://localhost:8000/progress/reset" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Neural Networks"
  }'

# Python
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/progress/reset",
        headers={"Authorization": f"Bearer {token}"},
        json={"topic": "Neural Networks"}
    )
    data = response.json()
    print(data['message'])

# JavaScript (fetch)
const response = await fetch('http://localhost:8000/progress/reset', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    topic: 'Neural Networks'
  })
});
const data = await response.json();
console.log(data.message);
```

---

## Complete Workflow Example

### Scenario: User completes a quiz

```python
import httpx

async def complete_quiz_workflow(token: str, user_id: str):
    """Complete workflow: quiz → evaluate → check progress"""
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 1: Get study material
        study_response = await client.post(
            "http://localhost:8000/study",
            headers=headers,
            json={"topics": ["Neural Networks"]}
        )
        study_package = study_response.json()
        
        # Step 2: User takes quiz (simulated answers)
        answers = ["A", "B", "C", "D", "A"]
        
        # Step 3: Evaluate quiz (auto-updates progress + awards XP)
        eval_response = await client.post(
            "http://localhost:8000/progress/evaluate",
            headers=headers,
            json={
                "study_package": study_package,
                "answers": answers
            }
        )
        result = eval_response.json()
        
        print(f"Score: {result['score_percentage']}%")
        print(f"XP Awarded: {result['xp_awarded']}")
        print(f"Total XP: {result['total_xp']}")
        
        # Step 4: Check complete progress
        progress_response = await client.get(
            f"http://localhost:8000/progress/{user_id}",
            headers=headers
        )
        progress = progress_response.json()
        
        print(f"Total Topics: {progress['statistics']['total_topics']}")
        print(f"Average Score: {progress['statistics']['average_score']}%")
        
        return progress
```

### Scenario: Award bonus XP for streak

```python
async def award_streak_bonus(token: str, streak_days: int):
    """Award XP for maintaining a daily streak"""
    
    points = 25 * (streak_days // 7)  # 25 XP per week
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/progress/update",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "points": points,
                "reason": "daily_streak",
                "metadata": {
                    "streak_days": streak_days,
                    "bonus_type": "weekly"
                }
            }
        )
        
        result = response.json()
        print(f"Streak bonus: {result['xp_log']['points']} XP")
        print(f"New total: {result['total_xp']} XP")
```

### Scenario: Reset and retry topic

```python
async def reset_and_retry(token: str, topic: str):
    """Reset a topic and start fresh"""
    
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Reset progress
        reset_response = await client.post(
            "http://localhost:8000/progress/reset",
            headers=headers,
            json={"topic": topic}
        )
        
        print(reset_response.json()['message'])
        
        # Start new study session
        study_response = await client.post(
            "http://localhost:8000/study",
            headers=headers,
            json={"topics": [topic]}
        )
        
        return study_response.json()
```

---

## Error Handling

### Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid JWT token |
| 403 | Forbidden | Accessing another user's data |
| 404 | Not Found | Topic doesn't exist |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Internal Server Error | Database/server issue |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Best Practices

1. **Always check response status** before parsing JSON
2. **Handle 401/403** by redirecting to login
3. **Validate input** before sending requests
4. **Retry 500 errors** with exponential backoff
5. **Log errors** for debugging

---

## Rate Limiting

Currently no rate limiting is implemented. Recommended limits for production:

- `GET` requests: 100 per minute per user
- `POST` requests: 30 per minute per user
- `POST /progress/update`: 10 per minute per user (prevent XP farming)

---

## Testing

Use the provided test script:

```bash
cd backend
python3 test_progress_endpoints.py
```

This will test all endpoints with various scenarios including:
- Successful operations
- Security checks (403 Forbidden)
- Validation errors (422)
- Not found errors (404)

---

## Database Changes

All operations update Supabase in real-time:

| Endpoint | Database Action |
|----------|-----------------|
| `/progress/{user_id}` | SELECT (read-only) |
| `/progress/update` | INSERT into xp_logs |
| `/progress/reset` | DELETE from progress |
| `/progress/evaluate` | INSERT/UPDATE progress + INSERT xp_logs |

Row Level Security (RLS) ensures users can only modify their own data.

---

## Frontend Integration Tips

### Display Total XP in Header

```javascript
async function loadUserXP(userId, token) {
  const response = await fetch(`/progress/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  document.getElementById('xp-display').textContent = 
    `${data.xp.total_xp} XP`;
}
```

### Show Progress Dashboard

```javascript
async function loadDashboard(userId, token) {
  const response = await fetch(`/progress/${userId}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  const data = await response.json();
  
  // Display stats
  const stats = data.statistics;
  console.log(`Completed: ${stats.completed_topics}/${stats.total_topics}`);
  console.log(`Average Score: ${stats.average_score}%`);
  
  // Display topics
  data.topics.forEach(topic => {
    console.log(`${topic.topic}: ${topic.completion_status} (${topic.avg_score}%)`);
  });
}
```

### Celebrate XP Gains

```javascript
async function celebrateXP(xpAwarded) {
  // Show animation/notification
  showNotification(`+${xpAwarded} XP! 🎉`);
  
  // Update display
  await loadUserXP(userId, token);
}
```

---

## Support

- **Documentation**: `/docs/progress-tracking.md`
- **Setup Guide**: `/docs/setup-progress-tables.md`
- **Test Script**: `/backend/test_progress_endpoints.py`
- **Migration**: `/backend/migrations/001_create_progress_xp_tables.sql`
