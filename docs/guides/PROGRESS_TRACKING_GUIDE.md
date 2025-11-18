# Progress Tracking System - Complete Guide

## 📊 Overview

The enhanced progress tracking system provides comprehensive user progress monitoring, XP history, and quiz analytics. This guide explains the database schema, API endpoints, and automatic update mechanisms.

---

## 🗄️ Database Schema

### Tables Structure

#### 1. **user_topics** - Topic Engagement Tracking
```sql
Columns:
- id: UUID (Primary Key)
- user_id: TEXT
- topic: TEXT
- status: TEXT (not_started, in_progress, completed, mastered)
- score: DECIMAL(5,2) - Latest quiz score
- best_score: DECIMAL(5,2) - Best score achieved
- attempts: INTEGER - Total quiz attempts
- time_spent: INTEGER - Time in seconds
- last_attempted_at: TIMESTAMPTZ
- completed_at: TIMESTAMPTZ
- created_at: TIMESTAMPTZ
- updated_at: TIMESTAMPTZ

Unique Constraint: (user_id, topic)
```

**Status Progression:**
- `not_started` → First quiz attempt → `in_progress`
- `in_progress` → Score ≥ 70% → `completed`
- `completed` → Score ≥ 90% → `mastered`

#### 2. **quiz_scores** - Individual Quiz Attempts
```sql
Columns:
- id: UUID (Primary Key)
- user_id: TEXT
- topic: TEXT
- difficulty: TEXT (easy, medium, hard, expert)
- correct: INTEGER - Correct answers
- total: INTEGER - Total questions
- score: DECIMAL(5,2) - Calculated percentage
- xp_gained: INTEGER - XP from this quiz
- time_taken: INTEGER - Seconds
- answers: JSONB - User's answers
- questions: JSONB - Quiz questions
- metadata: JSONB - Additional data
- created_at: TIMESTAMPTZ
```

#### 3. **xp_history** - Complete XP Change Log
```sql
Columns:
- id: UUID (Primary Key)
- user_id: TEXT
- xp_change: INTEGER - Delta (+ or -)
- reason: TEXT - Why XP changed
- topic: TEXT - Related topic
- quiz_id: UUID - Reference to quiz
- previous_xp: INTEGER - Before change
- new_xp: INTEGER - After change
- previous_level: INTEGER
- new_level: INTEGER
- metadata: JSONB
- created_at: TIMESTAMPTZ
```

#### 4. **Existing Tables** (Maintained for Compatibility)
- `users` - User profiles with total_xp and level
- `progress` - Legacy progress tracking
- `xp_logs` - Legacy XP logs
- `quiz_results` - Legacy quiz results

---

## 🔄 Automatic Updates

### Triggers & Auto-Updates

#### 1. **Quiz Score Auto-Calculation**
When a quiz is submitted:
```sql
-- Trigger: calculate_quiz_score()
-- Calculates: score = (correct / total) * 100
```

#### 2. **Topic Progress Auto-Update**
After quiz submission:
```sql
-- Trigger: update_topic_progress()
-- Updates:
--   - Latest score
--   - Best score (if improved)
--   - Attempts count (+1)
--   - Status (based on score)
--   - last_attempted_at timestamp
--   - completed_at (if newly completed)
```

Status Update Logic:
- Score ≥ 90% → `mastered`
- Score ≥ 70% → `completed`
- Score < 70% → `in_progress`

#### 3. **XP History Sync**
When XP is logged:
```sql
-- Trigger: sync_xp_to_history()
-- Creates: Complete xp_history record with before/after XP
```

---

## 🚀 API Endpoints

### Base URL: `/progress/v2`

### 1. **Submit Quiz**
```http
POST /progress/v2/submit-quiz
```

**Request Body:**
```json
{
  "user_id": "demo_user",
  "topic": "JavaScript Basics",
  "difficulty": "medium",
  "correct": 8,
  "total": 10,
  "time_taken": 180,
  "answers": ["A", "B", "C", "D", "A", "C", "B", "D", "A", "C"],
  "questions": [...],
  "metadata": {}
}
```

**Response:**
```json
{
  "success": true,
  "quiz_id": "uuid",
  "score": 80.0,
  "correct": 8,
  "total": 10,
  "xp_earned": 135,
  "xp_change": {
    "previous_xp": 2450,
    "new_xp": 2585,
    "previous_level": 5,
    "new_level": 6,
    "leveled_up": true
  },
  "feedback": "Great job! Solid understanding demonstrated! 👍"
}
```

**What Happens Automatically:**
1. ✅ Calculates score percentage
2. ✅ Calculates XP based on difficulty + score
3. ✅ Inserts into `quiz_scores`
4. ✅ Updates `user_topics` (via trigger)
5. ✅ Inserts into `xp_history`
6. ✅ Updates `users.total_xp` and `users.level`
7. ✅ Inserts into `xp_logs` (backward compatibility)

---

### 2. **Get User Progress**
```http
GET /progress/v2/user/{user_id}
```

**Response:**
```json
{
  "user": {
    "user_id": "demo_user",
    "username": "demo_user",
    "total_xp": 2585,
    "level": 6
  },
  "topics": [
    {
      "topic": "JavaScript Basics",
      "status": "mastered",
      "score": 92.0,
      "best_score": 95.0,
      "attempts": 15
    }
  ],
  "recent_xp_history": [...],
  "total_quizzes": 42,
  "stats": {
    "total_topics": 4,
    "mastered": 2,
    "completed": 1,
    "in_progress": 1,
    "avg_score": 87.5
  }
}
```

---

### 3. **Get User Topics**
```http
GET /progress/v2/user/{user_id}/topics
GET /progress/v2/user/{user_id}/topics?status=mastered
```

**Response:**
```json
{
  "user_id": "demo_user",
  "topics": [
    {
      "topic": "JavaScript Basics",
      "status": "mastered",
      "score": 92.0,
      "best_score": 95.0,
      "attempts": 15,
      "time_spent": 3600,
      "last_attempted_at": "2025-11-06T10:30:00Z"
    }
  ],
  "count": 4
}
```

---

### 4. **Get Topic Progress**
```http
GET /progress/v2/user/{user_id}/topics/{topic}
```

**Response:**
```json
{
  "progress": {
    "topic": "JavaScript Basics",
    "status": "mastered",
    "score": 92.0,
    "best_score": 95.0,
    "attempts": 15
  },
  "quiz_history": [
    {
      "id": "uuid",
      "score": 92.0,
      "difficulty": "medium",
      "xp_gained": 145,
      "created_at": "2025-11-06T10:30:00Z"
    }
  ],
  "total_attempts": 15
}
```

---

### 5. **Get XP History**
```http
GET /progress/v2/user/{user_id}/xp-history?limit=50
```

**Response:**
```json
{
  "user_id": "demo_user",
  "history": [
    {
      "xp_change": 135,
      "reason": "quiz_complete",
      "topic": "JavaScript Basics",
      "previous_xp": 2450,
      "new_xp": 2585,
      "previous_level": 5,
      "new_level": 6,
      "created_at": "2025-11-06T10:30:00Z"
    }
  ],
  "count": 50
}
```

---

### 6. **Get Quiz History**
```http
GET /progress/v2/user/{user_id}/quiz-history?limit=50
GET /progress/v2/user/{user_id}/quiz-history?topic=JavaScript+Basics
```

**Response:**
```json
{
  "user_id": "demo_user",
  "quizzes": [
    {
      "id": "uuid",
      "topic": "JavaScript Basics",
      "difficulty": "medium",
      "correct": 8,
      "total": 10,
      "score": 80.0,
      "xp_gained": 135,
      "time_taken": 180,
      "created_at": "2025-11-06T10:30:00Z"
    }
  ],
  "count": 42
}
```

---

### 7. **Get User Statistics**
```http
GET /progress/v2/user/{user_id}/stats
```

**Response:**
```json
{
  "user_id": "demo_user",
  "total_xp": 2585,
  "level": 6,
  "progress": {
    "total_topics": 4,
    "mastered_count": 2,
    "completed_count": 1,
    "in_progress_count": 1,
    "avg_best_score": 87.5,
    "total_attempts": 42,
    "total_time_spent": 7200
  }
}
```

---

### 8. **Get Leaderboard**
```http
GET /progress/v2/leaderboard?limit=10
```

**Response:**
```json
{
  "leaderboard": [
    {
      "user_id": "user_1",
      "username": "CodeMaster3000",
      "total_xp": 5420,
      "level": 11,
      "topics_attempted": 12,
      "total_quizzes": 85,
      "avg_score": 88.5,
      "last_quiz_at": "2025-11-06T09:15:00Z"
    }
  ],
  "count": 10
}
```

---

## 🧮 XP Calculation Formula

### Base XP
```
Base XP = 100 points (for completing any quiz)
```

### Difficulty Bonuses
```
easy    = +10 XP
medium  = +20 XP
hard    = +30 XP
expert  = +50 XP
```

### Score Tier Bonuses
```
100% (Perfect)  = +50 XP
90-99% (Excellent) = +30 XP
80-89% (Good)      = +15 XP
70-79% (Passing)   = +0 XP
< 70% (Failing)    = +0 XP
```

### Example Calculations

**Example 1: Medium difficulty, 80% score**
```
Base:       100 XP
Difficulty: +20 XP (medium)
Score:      +15 XP (80-89%)
Total:      135 XP
```

**Example 2: Hard difficulty, 100% score**
```
Base:       100 XP
Difficulty: +30 XP (hard)
Score:      +50 XP (perfect)
Total:      180 XP
```

**Example 3: Easy difficulty, 65% score**
```
Base:       100 XP
Difficulty: +10 XP (easy)
Score:      +0 XP (< 70%)
Total:      110 XP
```

---

## 🎮 Level System

### XP to Level Conversion
```
Level = (Total XP ÷ 500) + 1
```

### Level Thresholds
```
Level 1:  0 - 499 XP
Level 2:  500 - 999 XP
Level 3:  1000 - 1499 XP
Level 4:  1500 - 1999 XP
Level 5:  2000 - 2499 XP
Level 6:  2500 - 2999 XP
...and so on (500 XP per level)
```

---

## 📈 Database Views

### 1. **user_progress_summary**
Aggregated statistics per user:
```sql
SELECT * FROM user_progress_summary WHERE user_id = 'demo_user';
```

Returns:
- total_topics
- mastered_count
- completed_count
- in_progress_count
- avg_best_score
- total_attempts
- total_time_spent

### 2. **recent_quiz_activity**
Recent quiz completions across all users:
```sql
SELECT * FROM recent_quiz_activity LIMIT 10;
```

### 3. **xp_leaderboard_detailed**
Enhanced leaderboard with statistics:
```sql
SELECT * FROM xp_leaderboard_detailed LIMIT 10;
```

---

## 🔧 Setup Instructions

### 1. Run Database Migration
```bash
# In Supabase SQL Editor:
# 1. Run SUPABASE_SCHEMA.sql (main schema)
# 2. Run MIGRATION_PROGRESS_TRACKING.sql (this migration)
```

### 2. Verify Tables
```sql
-- Check tables exist
SELECT tablename FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('user_topics', 'quiz_scores', 'xp_history');

-- Check triggers exist
SELECT tgname FROM pg_trigger 
WHERE tgname LIKE '%quiz%' OR tgname LIKE '%xp%';
```

### 3. Test with Demo Data
```sql
-- View demo data
SELECT * FROM user_topics WHERE user_id = 'demo_user';
SELECT * FROM quiz_scores WHERE user_id = 'demo_user';
SELECT * FROM xp_history WHERE user_id = 'demo_user';
```

### 4. Update Backend
```bash
# Already included in main.py
# Routes available at /progress/v2/*
```

### 5. Test API
```bash
# Test quiz submission
curl -X POST http://localhost:8000/progress/v2/submit-quiz \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user",
    "topic": "Test Topic",
    "difficulty": "medium",
    "correct": 8,
    "total": 10
  }'
```

---

## 📊 Frontend Integration Example

### Submit Quiz
```typescript
const submitQuiz = async (quizData) => {
  const response = await fetch('/progress/v2/submit-quiz', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: 'demo_user',
      topic: quizData.topic,
      difficulty: quizData.difficulty,
      correct: quizData.correct,
      total: quizData.total,
      time_taken: quizData.timeInSeconds,
      answers: quizData.userAnswers,
      questions: quizData.questions
    })
  });
  
  const result = await response.json();
  
  if (result.success) {
    console.log(`Earned ${result.xp_earned} XP!`);
    if (result.xp_change.leveled_up) {
      showLevelUpAnimation(result.xp_change.new_level);
    }
  }
};
```

### Get User Progress
```typescript
const getUserProgress = async (userId) => {
  const response = await fetch(`/progress/v2/user/${userId}`);
  const data = await response.json();
  
  // Display user stats
  console.log(`Level ${data.user.level} - ${data.user.total_xp} XP`);
  console.log(`Topics: ${data.stats.total_topics}`);
  console.log(`Mastered: ${data.stats.mastered}`);
};
```

---

## ✅ Testing Checklist

- [ ] Run migration SQL successfully
- [ ] Verify all 3 new tables exist
- [ ] Check triggers are active
- [ ] Test quiz submission via API
- [ ] Verify automatic progress update
- [ ] Confirm XP history creation
- [ ] Test level-up scenario
- [ ] Verify status progression (in_progress → completed → mastered)
- [ ] Test all GET endpoints
- [ ] Check leaderboard works

---

## 🎉 Complete!

Your progress tracking system is now fully set up with:
- ✅ Detailed topic tracking
- ✅ Individual quiz attempt records
- ✅ Complete XP history with before/after
- ✅ Automatic progress updates
- ✅ Level system
- ✅ Comprehensive API endpoints
- ✅ Real-time capability

**Next Steps:**
1. Integrate frontend to use `/progress/v2` endpoints
2. Add real-time subscriptions for live updates
3. Build progress visualization dashboards
4. Add achievement system
