# Study Recommendation Agent - API Documentation

## Overview

The Study Recommendation Agent analyzes user performance data to provide personalized learning recommendations. It identifies weak areas, suggests reviews for stale topics, and recommends new learning opportunities.

---

## Features

- **Weak Area Analysis**: Identifies topics with scores below 70%
- **Stale Topic Detection**: Finds topics not studied in 7+ days
- **New Topic Suggestions**: Recommends unexplored subjects
- **Intelligent Prioritization**: 
  - High Priority: Weak areas (immediate improvement)
  - Medium Priority: Stale topics (knowledge retention)
  - Low Priority: New topics (knowledge expansion)
- **XP Estimation**: Predicts potential XP gain (120-225 XP)
- **AI-Enhanced Insights**: Personalized motivational messages and learning advice
- **Difficulty Matching**: Recommends appropriate difficulty based on current performance

---

## API Endpoint

### Get Study Recommendations

**Endpoint:** `GET /study/recommendations`

**Authentication:** Required (Bearer token)

**Description:** Generates personalized study recommendations based on user's complete learning history.

#### Query Parameters

```
max_recommendations (integer, optional): Maximum number of recommendations (default: 5)
include_ai_insights (boolean, optional): Enable AI-generated insights (default: true)
```

#### Request Example

```bash
curl -X GET "http://localhost:8000/study/recommendations?max_recommendations=5&include_ai_insights=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Response Schema

```json
{
  "recommendations": [
    {
      "topic": "Algorithms",
      "reason": "Improve performance (current: 45%, goal: 70%+)",
      "priority": "high",
      "category": "weak_area",
      "current_score": 45.0,
      "recommended_difficulty": "easy",
      "estimated_xp_gain": 132,
      "urgency": "Address gaps in understanding"
    }
  ],
  "ai_insights": {
    "motivational_message": "You're making great progress! Focus on your weak areas to accelerate your learning.",
    "learning_insight": "Your scores show consistent improvement in most topics, but Algorithms needs attention.",
    "priority_advice": "Start with the basics of Algorithms using easy-level quizzes to build confidence."
  },
  "overall_stats": {
    "total_attempts": 35,
    "avg_score": 68.5,
    "topics_studied": 8
  },
  "metadata": {
    "ai_enhanced": true,
    "generated_at": "2025-01-05T10:30:00Z"
  }
}
```

---

## Recommendation Categories

### 1. Weak Areas (Priority: HIGH)

**Criteria:**
- Average score < 70%
- Sorted by performance gap (biggest gaps first)

**Example:**
```json
{
  "topic": "Algorithms",
  "reason": "Improve performance (current: 45%, goal: 70%+)",
  "priority": "high",
  "category": "weak_area",
  "current_score": 45.0,
  "recommended_difficulty": "easy",
  "estimated_xp_gain": 132,
  "urgency": "Address gaps in understanding"
}
```

**When to Study:**
- Immediate priority
- Blocks progress in related topics
- Foundation for advanced concepts

### 2. Stale Topics (Priority: MEDIUM)

**Criteria:**
- Not studied in 7+ days
- Sorted by staleness (oldest first)

**Example:**
```json
{
  "topic": "Database Design",
  "reason": "Review needed (last attempt: 10 days ago)",
  "priority": "medium",
  "category": "review",
  "current_score": 75.0,
  "recommended_difficulty": "medium",
  "estimated_xp_gain": 150,
  "urgency": "Maintain knowledge retention"
}
```

**When to Study:**
- Prevent knowledge decay
- Reinforce understanding
- Periodic review sessions

### 3. New Topics (Priority: LOW)

**Criteria:**
- Never attempted by user
- Expands knowledge base

**Example:**
```json
{
  "topic": "Machine Learning",
  "reason": "Expand your knowledge base with new topic",
  "priority": "low",
  "category": "new_learning",
  "current_score": null,
  "recommended_difficulty": "medium",
  "estimated_xp_gain": 150,
  "urgency": "Broaden expertise"
}
```

**When to Study:**
- After mastering current topics
- Career development goals
- Personal interest

---

## XP Estimation Logic

### Base XP Calculation

```python
BASE_XP = 150  # Average XP per quiz

difficulty_multipliers = {
    'easy': 0.8,    # 120 XP
    'medium': 1.0,  # 150 XP
    'hard': 1.3,    # 195 XP
    'expert': 1.5   # 225 XP
}
```

### Improvement Bonus

For weak areas (score < 70%):
```python
improvement_bonus = (70 - current_score) * 0.5
total_xp = base_xp * difficulty_multiplier + improvement_bonus
```

### XP Range Examples

| Current Score | Difficulty | Base XP | Bonus | Total XP |
|--------------|------------|---------|-------|----------|
| 45% | easy | 120 | 12.5 | **132** |
| 62% | medium | 150 | 4 | **154** |
| 85% | hard | 195 | 0 | **195** |
| 90% | expert | 225 | 0 | **225** |
| None (new) | medium | 150 | 0 | **150** |

---

## Recommendation Algorithm

### Step 1: Data Analysis

```python
# Fetch user progress from Supabase
user_progress = fetch_from_database(user_id)

# Analyze three dimensions
weak_areas = analyze_weak_areas(user_progress)
stale_topics = analyze_stale_topics(user_progress)
new_topics = identify_new_topics(user_progress, all_topics)
```

### Step 2: Prioritization

```python
recommendations = []

# Priority 1: Weak areas (max 3)
recommendations.extend(weak_areas[:3])

# Priority 2: Stale topics (fill remaining slots)
recommendations.extend(stale_topics[:max - len(recommendations)])

# Priority 3: New topics (if slots available)
recommendations.extend(new_topics[:max - len(recommendations)])
```

### Step 3: Difficulty Assignment

```python
def assign_difficulty(score):
    if score < 50:
        return 'easy'      # Build confidence
    elif score < 70:
        return 'medium'    # Continue improving
    elif score < 85:
        return 'hard'      # Challenge yourself
    else:
        return 'expert'    # Master level
```

### Step 4: AI Enhancement

```python
# Generate personalized insights
ai_insights = generate_with_ai({
    'motivational_message': ...,
    'learning_insight': ...,
    'priority_advice': ...
})
```

---

## Usage Examples

### Example 1: New User

**User Stats:**
- Total attempts: 0
- Topics studied: 0

**Response:**
```json
{
  "recommendations": [
    {
      "topic": "Python Programming",
      "reason": "Great starting point for beginners",
      "priority": "high",
      "category": "new_learning",
      "recommended_difficulty": "easy",
      "estimated_xp_gain": 120
    },
    {
      "topic": "Web Development",
      "reason": "Popular and practical skill",
      "priority": "medium",
      "category": "new_learning",
      "recommended_difficulty": "easy",
      "estimated_xp_gain": 120
    }
  ],
  "ai_insights": {
    "motivational_message": "Welcome to StudyQuest! Start with the basics and build your knowledge step by step."
  },
  "overall_stats": {
    "total_attempts": 0,
    "avg_score": 0,
    "topics_studied": 0
  }
}
```

### Example 2: Struggling Student

**User Stats:**
- Algorithms: 45% (5 attempts)
- System Design: 62% (3 attempts)
- Total avg: 53.5%

**Response:**
```json
{
  "recommendations": [
    {
      "topic": "Algorithms",
      "reason": "Improve performance (current: 45%, goal: 70%+)",
      "priority": "high",
      "category": "weak_area",
      "current_score": 45.0,
      "recommended_difficulty": "easy",
      "estimated_xp_gain": 132
    },
    {
      "topic": "System Design",
      "reason": "Improve performance (current: 62%, goal: 70%+)",
      "priority": "high",
      "category": "weak_area",
      "current_score": 62.0,
      "recommended_difficulty": "medium",
      "estimated_xp_gain": 154
    }
  ],
  "ai_insights": {
    "motivational_message": "Don't be discouraged! Focus on fundamentals in Algorithms to build a strong foundation.",
    "learning_insight": "Your struggles with Algorithms are normal for beginners. Take it step by step.",
    "priority_advice": "Start with easy-level Algorithms quizzes focusing on basic concepts like sorting and searching."
  }
}
```

### Example 3: Experienced Learner

**User Stats:**
- Python: 88% (last: today)
- JavaScript: 85% (last: 2 days ago)
- Database Design: 75% (last: 12 days ago)
- Web Development: 70% (last: 18 days ago)

**Response:**
```json
{
  "recommendations": [
    {
      "topic": "Web Development",
      "reason": "Review needed (last attempt: 18 days ago)",
      "priority": "medium",
      "category": "review",
      "current_score": 70.0,
      "recommended_difficulty": "medium",
      "estimated_xp_gain": 150
    },
    {
      "topic": "Database Design",
      "reason": "Review needed (last attempt: 12 days ago)",
      "priority": "medium",
      "category": "review",
      "current_score": 75.0,
      "recommended_difficulty": "medium",
      "estimated_xp_gain": 150
    },
    {
      "topic": "Machine Learning",
      "reason": "Expand your knowledge base with new topic",
      "priority": "low",
      "category": "new_learning",
      "recommended_difficulty": "medium",
      "estimated_xp_gain": 150
    }
  ],
  "ai_insights": {
    "motivational_message": "Excellent progress! Keep your skills sharp with regular reviews while exploring new topics.",
    "learning_insight": "You excel at Python and JavaScript. Time to maintain those skills and expand into new areas.",
    "priority_advice": "Review Web Development to prevent knowledge decay, then explore Machine Learning."
  }
}
```

---

## Frontend Integration

### React Example

```javascript
import { useState, useEffect } from 'react';

function StudyRecommendations() {
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchRecommendations();
  }, []);
  
  const fetchRecommendations = async () => {
    const response = await fetch(
      '/study/recommendations?max_recommendations=5&include_ai_insights=true',
      {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    );
    
    const data = await response.json();
    setRecommendations(data);
    setLoading(false);
  };
  
  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'red';
      case 'medium': return 'orange';
      case 'low': return 'green';
      default: return 'gray';
    }
  };
  
  const startQuiz = (topic, difficulty) => {
    // Navigate to quiz with recommended difficulty
    window.location.href = `/quiz?topic=${topic}&difficulty=${difficulty}`;
  };
  
  if (loading) return <div>Loading recommendations...</div>;
  
  return (
    <div className="recommendations">
      <h2>Your Personalized Study Recommendations</h2>
      
      {/* AI Insights */}
      {recommendations.ai_insights && (
        <div className="ai-insights">
          <h3>💡 AI Insights</h3>
          <p className="motivational">
            {recommendations.ai_insights.motivational_message}
          </p>
          <p className="insight">
            {recommendations.ai_insights.learning_insight}
          </p>
          <p className="advice">
            <strong>Priority:</strong> {recommendations.ai_insights.priority_advice}
          </p>
        </div>
      )}
      
      {/* Overall Stats */}
      {recommendations.overall_stats && (
        <div className="stats">
          <div>Total Quizzes: {recommendations.overall_stats.total_attempts}</div>
          <div>Avg Score: {recommendations.overall_stats.avg_score}%</div>
          <div>Topics: {recommendations.overall_stats.topics_studied}</div>
        </div>
      )}
      
      {/* Recommendations */}
      <div className="recommendation-list">
        {recommendations.recommendations.map((rec, index) => (
          <div 
            key={index} 
            className={`recommendation priority-${rec.priority}`}
          >
            <div className="header">
              <h3>{rec.topic}</h3>
              <span 
                className="priority-badge"
                style={{ color: getPriorityColor(rec.priority) }}
              >
                {rec.priority.toUpperCase()}
              </span>
            </div>
            
            <p className="reason">{rec.reason}</p>
            <p className="urgency">⚡ {rec.urgency}</p>
            
            <div className="details">
              <div>Category: {rec.category}</div>
              {rec.current_score !== null && (
                <div>Current Score: {rec.current_score}%</div>
              )}
              <div>Difficulty: {rec.recommended_difficulty}</div>
              <div>Est. XP: {rec.estimated_xp_gain}</div>
            </div>
            
            <button onClick={() => startQuiz(rec.topic, rec.recommended_difficulty)}>
              Start Quiz →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Configuration

### Environment Variables

```bash
# AI Enhancement (optional)
GEMINI_API_KEY=your_api_key

# Database (required)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Customizable Parameters

**In `recommendation_agent.py`:**

```python
class RecommendationAgent:
    # Thresholds
    WEAK_AREA_THRESHOLD = 70  # Scores below this are "weak"
    STALE_DAYS = 7            # Days before topic is "stale"
    MIN_ATTEMPTS_FOR_MASTERY = 3  # Attempts before considering mastered
    
    # XP Estimation
    BASE_XP_ESTIMATE = 150    # Base XP per quiz
    DIFFICULTY_MULTIPLIERS = {
        'easy': 0.8,
        'medium': 1.0,
        'hard': 1.3,
        'expert': 1.5
    }
```

---

## Best Practices

### For Students

1. **Follow Priority Order**: Address high-priority (weak areas) first
2. **Regular Reviews**: Don't let topics go stale (7+ days)
3. **Gradual Expansion**: Master current topics before adding new ones
4. **Use Estimated XP**: Plan study sessions around XP goals
5. **Trust AI Insights**: Personalized advice based on your patterns

### For Educators

1. **Monitor Weak Areas**: Provide additional resources for common struggles
2. **Encourage Reviews**: Remind students about stale topics
3. **Set XP Goals**: Use XP estimates for assignment planning
4. **Review Priorities**: Check if students are following recommendations
5. **Analyze Patterns**: Identify topics that frequently appear as weak areas

---

## Error Handling

### Common Errors

**1. No Recommendations (New User)**
```json
{
  "recommendations": [...],
  "metadata": {
    "new_user": true
  }
}
```
**Solution:** System provides default starter topics

**2. Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```
**Solution:** Include valid Bearer token

**3. Database Error**
```json
{
  "detail": "Failed to generate recommendations: [error]"
}
```
**Solution:** Check Supabase connection and credentials

---

## Data Flow

```
1. User Request
   ↓
2. Fetch User Data from Supabase
   ├─> progress table (avg_score, total_attempts, last_attempt)
   └─> xp_logs table (learning velocity)
   ↓
3. Analyze Performance
   ├─> Identify weak areas (score < 70%)
   ├─> Find stale topics (>7 days)
   └─> List new topics (not attempted)
   ↓
4. Prioritize Recommendations
   ├─> High: Weak areas (fill first)
   ├─> Medium: Stale topics (next)
   └─> Low: New topics (last)
   ↓
5. Estimate XP Gains
   ├─> Base XP × difficulty multiplier
   └─> + improvement bonus (if weak area)
   ↓
6. AI Enhancement (optional)
   ├─> Motivational message
   ├─> Learning insights
   └─> Priority advice
   ↓
7. Return Formatted Response
```

---

## Testing

### Run Test Suite

```bash
cd backend
source venv/bin/activate
python3 test_recommendations.py
```

**Expected Output:**
```
🎉 ALL 7 TESTS PASSED! Recommendation system is working correctly.
```

### Test Coverage

- ✅ Weak area detection and sorting
- ✅ Stale topic identification
- ✅ New topic suggestions
- ✅ XP estimation accuracy
- ✅ Recommendation prioritization
- ✅ Difficulty assignment
- ✅ Edge case handling

---

## Performance Metrics

The system tracks:

| Metric | Purpose |
|--------|---------|
| Weak Areas Count | Topics needing improvement |
| Stale Topics Count | Topics needing review |
| New Topics Available | Expansion opportunities |
| Avg Score | Overall performance level |
| Total Attempts | Learning engagement |
| Learning Velocity | Improvement rate |

---

## FAQ

**Q: How often should I check recommendations?**
A: After completing each quiz or weekly for active learners.

**Q: Why are my recommendations not changing?**
A: Complete quizzes to update your performance data.

**Q: Can I ignore low-priority recommendations?**
A: Yes, focus on high and medium priorities first.

**Q: What if I disagree with the difficulty?**
A: Use the adaptive quiz endpoint with difficulty_preference override.

**Q: How is "stale" determined?**
A: Topics not studied in 7+ days are considered stale.

**Q: Why doesn't my new topic have a current score?**
A: You haven't attempted it yet; score will appear after first quiz.

**Q: Can I customize the recommendation threshold?**
A: Yes, modify `WEAK_AREA_THRESHOLD` in `recommendation_agent.py`.

---

## Related Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /study/recommendations` | Get personalized recommendations |
| `POST /study/adaptive-quiz` | Start adaptive quiz |
| `POST /progress/evaluate` | Submit quiz results |
| `GET /progress/{user_id}` | View progress data |

---

**Last Updated:** January 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
