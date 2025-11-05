# Progress Tracking & XP System

This document describes the progress tracking and XP (Experience Points) gamification system in StudyQuest.

## Overview

The system tracks user progress across study topics and rewards engagement through an XP points system. This provides:

- **Progress Tracking**: Monitor completion status, scores, and attempts per topic
- **Gamification**: Earn XP points for completing quizzes and study activities
- **Analytics**: View detailed statistics and performance history

## Database Schema

### Progress Table

Tracks user progress for each study topic.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Reference to auth.users (with cascade delete) |
| `topic` | TEXT | Study topic name |
| `completion_status` | TEXT | Status: 'not_started', 'in_progress', 'completed' |
| `last_attempt` | TIMESTAMPTZ | Timestamp of last quiz attempt |
| `avg_score` | DECIMAL(5,2) | Average quiz score (0.00 - 100.00) |
| `total_attempts` | INTEGER | Number of quiz attempts for this topic |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

**Constraints:**
- Unique constraint on (user_id, topic) - one record per user per topic
- Foreign key to auth.users with CASCADE DELETE

### XP Logs Table

Tracks all XP-earning activities for gamification.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Reference to auth.users (with cascade delete) |
| `points` | INTEGER | XP points earned |
| `reason` | TEXT | Activity type (quiz_completed, study_session, etc.) |
| `metadata` | JSONB | Additional data (score, topic, duration, etc.) |
| `timestamp` | TIMESTAMPTZ | When XP was earned |

**Constraints:**
- Foreign key to auth.users with CASCADE DELETE

### User Total XP View

Aggregated view for quick XP lookup.

```sql
CREATE VIEW user_total_xp AS
SELECT 
  user_id,
  SUM(points) as total_xp,
  COUNT(*) as total_activities,
  MAX(timestamp) as last_activity
FROM xp_logs
GROUP BY user_id;
```

## XP Point Values

Default XP rewards for different activities:

| Activity | Points | Description |
|----------|--------|-------------|
| `quiz_completed` | 100 | Base points for completing a quiz |
| `perfect_score` | 50 | Bonus for 100% score |
| `study_session` | 50 | Completing a study session |
| `daily_streak` | 25 | Daily engagement bonus |
| `first_topic` | 150 | Bonus for first topic studied |
| `topic_completed` | 200 | Completing a topic (70%+ avg score) |

## API Endpoints

### Progress Endpoints

#### Get Progress Statistics
```
GET /progress/stats
Authorization: Bearer <token>
```

**Response:**
```json
{
  "total_topics": 5,
  "completed_topics": 2,
  "in_progress_topics": 3,
  "average_score": 78.5,
  "completion_rate": 40.0
}
```

#### Get All Topics Progress
```
GET /progress/topics
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "uuid",
  "total_topics": 3,
  "topics": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "topic": "Neural Networks",
      "completion_status": "completed",
      "last_attempt": "2025-11-05T10:30:00Z",
      "avg_score": 85.5,
      "total_attempts": 2,
      "created_at": "2025-11-04T09:00:00Z",
      "updated_at": "2025-11-05T10:30:00Z"
    }
  ]
}
```

#### Get Specific Topic Progress
```
GET /progress/topics/{topic}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "topic": "Neural Networks",
  "completion_status": "completed",
  "last_attempt": "2025-11-05T10:30:00Z",
  "avg_score": 85.5,
  "total_attempts": 2,
  "created_at": "2025-11-04T09:00:00Z",
  "updated_at": "2025-11-05T10:30:00Z"
}
```

#### Evaluate Quiz (with Progress Update)
```
POST /progress/evaluate
Authorization: Bearer <token>
Content-Type: application/json
```

**Request:**
```json
{
  "study_package": {
    "topic": "Neural Networks",
    "notes": { "title": "...", "key_points": [...] },
    "quiz": [...]
  },
  "answers": ["A", "B", "C", "D", "A"]
}
```

**Response:**
```json
{
  "topic": "Neural Networks",
  "total_questions": 5,
  "correct_answers": 4,
  "score_percentage": 80.0,
  "feedback": "Great job! You got 4 out of 5 questions correct...",
  "results": [...],
  "xp_awarded": 100,
  "total_xp": 450,
  "completion_status": "completed"
}
```

### XP Endpoints

#### Get Total XP
```
GET /progress/xp
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "uuid",
  "total_xp": 450,
  "total_activities": 5,
  "last_activity": "2025-11-05T10:30:00Z"
}
```

#### Get XP Logs
```
GET /progress/xp/logs?limit=50
Authorization: Bearer <token>
```

**Response:**
```json
{
  "user_id": "uuid",
  "count": 5,
  "logs": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "points": 100,
      "reason": "quiz_completed",
      "metadata": {
        "topic": "Neural Networks",
        "score": 80.0,
        "total_questions": 5,
        "correct_answers": 4,
        "completion_status": "completed"
      },
      "timestamp": "2025-11-05T10:30:00Z"
    }
  ]
}
```

## Row Level Security (RLS)

All tables have RLS enabled with user-specific policies:

### Progress Table Policies
- **SELECT**: Users can view their own progress
- **INSERT**: Users can create their own progress records
- **UPDATE**: Users can update their own progress records
- **DELETE**: Users can delete their own progress records

### XP Logs Table Policies
- **SELECT**: Users can view their own XP logs
- **INSERT**: Users can insert their own XP logs (backend also uses service role)

## Helper Functions

### update_progress_after_quiz()

Updates progress record after quiz completion, calculating running average score.

```sql
SELECT update_progress_after_quiz(
  p_user_id := 'uuid',
  p_topic := 'Neural Networks',
  p_score := 85.0,
  p_completion_status := 'completed'
);
```

### award_xp()

Awards XP points to a user with metadata tracking.

```sql
SELECT award_xp(
  p_user_id := 'uuid',
  p_points := 100,
  p_reason := 'quiz_completed',
  p_metadata := '{"topic": "Neural Networks", "score": 85.0}'::jsonb
);
```

## Python Utilities

### ProgressTracker Class

```python
from utils.progress_tracker import ProgressTracker

# Update progress
progress = await ProgressTracker.update_progress(
    user_id="uuid",
    topic="Neural Networks",
    score=85.0,
    completion_status="completed"
)

# Get user progress
progress_list = await ProgressTracker.get_user_progress(user_id="uuid")

# Get progress stats
stats = await ProgressTracker.get_progress_stats(user_id="uuid")
```

### XPTracker Class

```python
from utils.progress_tracker import XPTracker

# Award XP
xp_log = await XPTracker.award_xp(
    user_id="uuid",
    reason="quiz_completed",
    points=100,
    metadata={"topic": "Neural Networks", "score": 85.0}
)

# Get total XP
total = await XPTracker.get_total_xp(user_id="uuid")

# Get XP logs
logs = await XPTracker.get_user_xp_logs(user_id="uuid", limit=50)

# Process quiz completion (updates progress + awards XP)
result = await XPTracker.process_quiz_completion(
    user_id="uuid",
    topic="Neural Networks",
    score=85.0,
    total_questions=5,
    correct_answers=4
)
```

## Completion Status Logic

Topics are marked as:
- **not_started**: No quiz attempts yet
- **in_progress**: Quiz attempted but avg score < 70%
- **completed**: Average score >= 70%

## Score Calculation

Average score is calculated as a running average:

```
new_avg = ((current_avg × current_attempts) + new_score) / (current_attempts + 1)
```

## XP Calculation for Quizzes

```python
base_xp = 100  # quiz_completed
if score >= 100.0:
    base_xp += 50  # perfect_score bonus
if is_first_topic:
    base_xp += 150  # first_topic bonus

total_xp = base_xp
```

## Database Setup

Run the migration file to create all tables, indexes, and functions:

```sql
-- Run in Supabase SQL Editor
-- File: backend/migrations/001_create_progress_xp_tables.sql
```

## Indexes

Optimized indexes for common queries:

```sql
-- Progress table
CREATE INDEX idx_progress_user_id ON progress(user_id);
CREATE INDEX idx_progress_topic ON progress(topic);
CREATE INDEX idx_progress_user_topic ON progress(user_id, topic);

-- XP logs table
CREATE INDEX idx_xp_logs_user_id ON xp_logs(user_id);
CREATE INDEX idx_xp_logs_timestamp ON xp_logs(timestamp DESC);
CREATE INDEX idx_xp_logs_user_timestamp ON xp_logs(user_id, timestamp DESC);
```

## Frontend Integration

The frontend can use these endpoints to:

1. **Dashboard**: Display total XP, progress stats, recent activities
2. **Topic Cards**: Show completion status, average score per topic
3. **Progress History**: List all topics with progress bars
4. **XP Feed**: Show recent XP earnings with reasons
5. **Quiz Results**: Display XP earned after quiz completion

## Security Notes

- All endpoints require JWT authentication
- RLS policies ensure users can only access their own data
- Backend can use service role key to bypass RLS when needed
- Input validation prevents invalid scores or status values
- Unique constraint prevents duplicate progress records per topic
