# Adaptive Quiz API Documentation

## Overview

The Adaptive Quiz System automatically adjusts quiz difficulty based on a user's past performance, creating a personalized learning experience that adapts to each student's skill level.

## Features

- **Performance-Based Difficulty Adjustment**: Automatically increases/decreases difficulty based on quiz scores
- **Four Difficulty Levels**: Easy, Medium, Hard, Expert
- **Intelligent Thresholds**: 
  - Score ≥ 80% → Increase difficulty
  - Score < 50% → Decrease difficulty
  - Score 50-79% → Maintain current difficulty
- **User Preference Override**: Users can manually select difficulty
- **Temperature-Based Question Generation**: Higher difficulty = more creative/complex questions
- **Detailed Performance Tracking**: Integration with Supabase for historical data

---

## API Endpoints

### Generate Adaptive Quiz

**Endpoint:** `POST /study/adaptive-quiz`

**Authentication:** Required (Bearer token)

**Description:** Generates a quiz with difficulty automatically adjusted based on the user's performance history.

#### Request Body

```json
{
  "topic": "Machine Learning",
  "difficulty_preference": "hard",
  "num_questions": 5,
  "notes": "Optional study notes..."
}
```

**Fields:**
- `topic` (string, required): The subject/topic for the quiz
- `difficulty_preference` (string, optional): Override automatic difficulty selection
  - Valid values: `"easy"`, `"medium"`, `"hard"`, `"expert"`
  - If omitted, difficulty is determined automatically
- `num_questions` (integer, optional): Number of questions (default: 5)
- `notes` (string, optional): Custom study material. If omitted, notes are generated automatically

#### Response

```json
{
  "topic": "Machine Learning",
  "difficulty": "hard",
  "questions": [
    {
      "question": "Given a dataset with high dimensionality...",
      "options": {
        "A": "Principal Component Analysis",
        "B": "Linear Regression",
        "C": "K-Means Clustering",
        "D": "Decision Trees"
      },
      "correct_answer": "A",
      "explanation": "PCA is specifically designed to reduce..."
    }
  ],
  "adaptive_metadata": {
    "user_performance": {
      "avg_score": 85.5,
      "total_attempts": 12,
      "last_difficulty": "medium"
    },
    "recommended_difficulty": "hard",
    "reasoning": "Your average score of 85.5% shows strong mastery. Ready to challenge yourself at hard level.",
    "adjusted_from": "medium"
  },
  "model": "google/gemini-2.0-flash-exp:free",
  "cognitive_level": "evaluating and creating"
}
```

**Response Fields:**
- `topic`: The quiz topic
- `difficulty`: The selected difficulty level
- `questions`: Array of quiz questions (see Question Format below)
- `adaptive_metadata`: Information about the adaptive selection
  - `user_performance`: User's historical performance data
  - `recommended_difficulty`: AI-recommended difficulty
  - `reasoning`: Explanation for difficulty choice
  - `adjusted_from`: Previous difficulty (if changed)
- `model`: AI model used for generation
- `cognitive_level`: Target cognitive complexity

---

## Difficulty Levels

### Easy
- **Cognitive Level:** Remembering and Understanding
- **Question Types:** Recall, definitions, basic concepts
- **Temperature:** 0.6 (more consistent)
- **Characteristics:**
  - Straightforward, clear definitions
  - Simple vocabulary, direct questions
  - Includes helpful hints

### Medium
- **Cognitive Level:** Applying and Analyzing
- **Question Types:** Application, analysis, scenarios
- **Temperature:** 0.7 (balanced)
- **Characteristics:**
  - Scenario-based questions
  - Moderate vocabulary, some inference needed
  - Minimal hints, focus on understanding

### Hard
- **Cognitive Level:** Evaluating and Creating
- **Question Types:** Evaluation, synthesis, comparison
- **Temperature:** 0.8 (more creative)
- **Characteristics:**
  - Complex scenarios, concept comparison
  - Advanced vocabulary, multi-step reasoning
  - No hints, tests deep understanding

### Expert
- **Cognitive Level:** Analyzing Complex Systems and Creating Solutions
- **Question Types:** Problem-solving, critical thinking, edge cases
- **Temperature:** 0.85 (most creative)
- **Characteristics:**
  - Real-world problems, edge cases
  - Technical terminology
  - Requires synthesis of multiple concepts
  - Expects mastery-level knowledge

---

## Adaptive Logic

### Difficulty Determination Algorithm

```python
def determine_next_difficulty(current_difficulty, avg_score, user_preference):
    # User preference overrides automatic selection
    if user_preference:
        return user_preference
    
    # New users default to medium
    if not current_difficulty or avg_score is None:
        return "medium"
    
    # Increase difficulty for high performers
    if avg_score >= 80:
        return increase_difficulty(current_difficulty)
    
    # Decrease difficulty for struggling students
    elif avg_score < 50:
        return decrease_difficulty(current_difficulty)
    
    # Maintain current difficulty
    else:
        return current_difficulty
```

### Performance Thresholds

| Score Range | Action | Reasoning |
|------------|--------|-----------|
| ≥ 80% | Increase difficulty | Strong mastery, ready for challenge |
| 50-79% | Maintain difficulty | Optimal learning zone |
| < 50% | Decrease difficulty | Need more practice at current level |

### Difficulty Progression

```
easy → medium → hard → expert
 ↑        ↑       ↑        ↑
 └────────┴───────┴────────┘
         Can move both ways
```

- Users can move up or down based on performance
- Cannot go above "expert" or below "easy"
- Gradual progression (one level at a time)

---

## Usage Examples

### Example 1: New User (Automatic Difficulty)

**Request:**
```bash
curl -X POST "http://localhost:8000/study/adaptive-quiz" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Programming",
    "num_questions": 5
  }'
```

**Expected Behavior:**
- System defaults to "medium" difficulty (new user, no history)
- Reasoning: "Welcome! Starting at medium difficulty. We'll adjust based on your performance."

---

### Example 2: High Performer (Automatic Increase)

**User History:**
- Average score: 88%
- Last difficulty: "medium"
- Total quizzes: 10

**Request:**
```bash
curl -X POST "http://localhost:8000/study/adaptive-quiz" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Data Structures",
    "num_questions": 7
  }'
```

**Expected Behavior:**
- System increases difficulty to "hard"
- Reasoning: "Your average score of 88.0% shows strong mastery. Ready to challenge yourself at hard level."
- Questions will be more complex, requiring synthesis and evaluation

---

### Example 3: Struggling Student (Automatic Decrease)

**User History:**
- Average score: 42%
- Last difficulty: "hard"
- Total quizzes: 5

**Request:**
```bash
curl -X POST "http://localhost:8000/study/adaptive-quiz" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Algorithms",
    "num_questions": 5
  }'
```

**Expected Behavior:**
- System decreases difficulty to "medium"
- Reasoning: "Your average score of 42.0% suggests you need more practice. Trying medium level will help build confidence."
- Additional note: "Complete more quizzes for better difficulty calibration."

---

### Example 4: User Preference Override

**Request:**
```bash
curl -X POST "http://localhost:8000/study/adaptive-quiz" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Database Design",
    "difficulty_preference": "expert",
    "num_questions": 5
  }'
```

**Expected Behavior:**
- System uses "expert" difficulty (user preference)
- Overrides automatic recommendation
- Useful for confident learners or specific practice

---

## Question Format

Each question in the response follows this structure:

```json
{
  "question": "What is the time complexity of binary search?",
  "options": {
    "A": "O(n)",
    "B": "O(log n)",
    "C": "O(n^2)",
    "D": "O(1)"
  },
  "correct_answer": "B",
  "explanation": "Binary search divides the search space in half with each iteration, resulting in logarithmic time complexity O(log n). This is significantly faster than linear search O(n) for large datasets."
}
```

**Question Characteristics by Difficulty:**

**Easy:**
```json
{
  "question": "What does HTML stand for?",
  "options": {
    "A": "Hyper Text Markup Language",
    "B": "High Tech Modern Language",
    "C": "Home Tool Markup Language",
    "D": "Hyperlinks and Text Markup Language"
  }
}
```

**Expert:**
```json
{
  "question": "Given a distributed system with eventual consistency, how would you implement a conflict resolution strategy for concurrent updates to the same data item across multiple nodes, considering both last-write-wins and application-specific merge functions?",
  "options": {
    "A": "Use vector clocks with custom merge functions...",
    "B": "Implement Paxos consensus protocol...",
    "C": "Apply CRDTs with commutative operations...",
    "D": "Enforce strict serialization with distributed locks..."
  }
}
```

---

## Integration with Progress Tracking

The adaptive quiz system integrates with the Progress API:

### 1. Fetching User Performance

```python
# Backend automatically queries:
# - `progress` table: avg_score, total_attempts
# - `xp_logs` table: last_difficulty from metadata
```

### 2. Recording Quiz Results

After quiz completion, use the Progress API to record results:

```bash
POST /progress/evaluate
{
  "quiz_type": "adaptive",
  "score": 85,
  "difficulty": "hard",
  "max_score": 100
}
```

This updates:
- User's average score
- XP points (with difficulty bonus)
- Difficulty history for next adaptive quiz

---

## Frontend Integration

### React Example

```javascript
import { useState, useEffect } from 'react';

function AdaptiveQuiz() {
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const generateQuiz = async (topic, preferredDifficulty = null) => {
    setLoading(true);
    
    const response = await fetch('/study/adaptive-quiz', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        topic,
        difficulty_preference: preferredDifficulty,
        num_questions: 5
      })
    });
    
    const data = await response.json();
    setQuiz(data);
    setLoading(false);
  };
  
  const showAdaptiveInfo = () => {
    const { adaptive_metadata } = quiz;
    return (
      <div className="adaptive-info">
        <h3>Difficulty: {quiz.difficulty.toUpperCase()}</h3>
        <p>{adaptive_metadata.reasoning}</p>
        {adaptive_metadata.adjusted_from && (
          <p>📈 Moved from {adaptive_metadata.adjusted_from} to {quiz.difficulty}</p>
        )}
        <p>Average Score: {adaptive_metadata.user_performance.avg_score}%</p>
        <p>Quizzes Completed: {adaptive_metadata.user_performance.total_attempts}</p>
      </div>
    );
  };
  
  return (
    <div>
      {quiz && showAdaptiveInfo()}
      {/* Render quiz questions */}
    </div>
  );
}
```

---

## Performance Metrics

The system tracks and uses these metrics:

| Metric | Source | Usage |
|--------|--------|-------|
| Average Score | `progress` table | Primary difficulty adjustment |
| Total Attempts | `progress` table | Reliability of avg_score |
| Last Difficulty | `xp_logs` metadata | Starting point for adjustment |
| Topic Performance | `progress` table | Topic-specific calibration |

---

## Best Practices

### For Students

1. **Trust the System**: The adaptive algorithm is designed to keep you in the optimal learning zone
2. **Complete Multiple Quizzes**: At least 3-5 quizzes for accurate difficulty calibration
3. **Use Preferences Sparingly**: Let the system adjust automatically for best results
4. **Review Explanations**: Especially at higher difficulties, explanations are crucial
5. **Track Progress**: Watch your avg_score improve over time

### For Educators

1. **Monitor Difficulty Distribution**: Ensure students aren't stuck at one level
2. **Review Thresholds**: 80% increase / 50% decrease can be adjusted if needed
3. **Encourage Consistency**: Regular quizzing improves adaptive accuracy
4. **Provide Resources**: Link additional materials for students at lower difficulties
5. **Celebrate Progress**: Highlight when students move up difficulty levels

---

## Error Handling

### Common Errors

**1. Unauthorized**
```json
{
  "detail": "Not authenticated"
}
```
**Solution:** Include valid Bearer token

**2. Invalid Difficulty**
```json
{
  "detail": "Invalid difficulty preference. Must be one of: easy, medium, hard, expert"
}
```
**Solution:** Use valid difficulty values

**3. Empty Topic**
```json
{
  "detail": "Topic cannot be empty"
}
```
**Solution:** Provide a valid topic string

**4. Generation Failure**
```json
{
  "detail": "Failed to generate adaptive quiz: [error details]"
}
```
**Solution:** Check API keys, network, try again

---

## Testing

### Test Script

Run the adaptive quiz tests:

```bash
cd /Users/mohith/Projects/StudyQuest/backend
source venv/bin/activate
python3 test_adaptive_quiz.py
```

**Expected Output:**
```
🎉 ALL TESTS PASSED! Adaptive quiz system is working correctly.
```

### Manual Testing Scenarios

1. **New User Test**: Create new user, should default to medium
2. **High Performer Test**: Score > 80% consistently, should increase difficulty
3. **Low Performer Test**: Score < 50% consistently, should decrease difficulty
4. **Preference Override Test**: Set difficulty_preference, should use that value
5. **Boundary Test**: Test scores at exactly 50%, 80%

---

## Configuration

### Environment Variables

```bash
# Required for quiz generation
OPENROUTER_API_KEY=your_api_key_here

# Supabase (for user performance data)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Customization

To modify thresholds, edit `backend/agents/adaptive_quiz_agent.py`:

```python
class AdaptiveQuizAgent:
    INCREASE_THRESHOLD = 80  # Change to adjust when difficulty increases
    DECREASE_THRESHOLD = 50  # Change to adjust when difficulty decreases
```

To modify temperature settings, edit `get_difficulty_context()`:

```python
'easy': {
    'temperature': 0.6,  # Lower = more consistent
    ...
}
```

---

## Changelog

### Version 1.0 (Current)
- ✅ Four difficulty levels (easy, medium, hard, expert)
- ✅ Automatic difficulty adjustment (80% increase / 50% decrease)
- ✅ User preference override
- ✅ Temperature-based question generation
- ✅ Integration with Supabase progress tracking
- ✅ Detailed reasoning for difficulty changes
- ✅ Comprehensive test suite

### Future Enhancements
- 🔄 Topic-specific difficulty (different difficulty per subject)
- 🔄 Time-based difficulty decay (reduce difficulty if inactive)
- 🔄 Peer comparison (difficulty relative to class average)
- 🔄 Learning velocity tracking (rate of improvement)

---

## FAQ

**Q: How many quizzes before difficulty adjusts?**
A: Difficulty can adjust after every quiz, but the system provides more accurate recommendations after 3+ quizzes.

**Q: Can I skip difficulty levels?**
A: No, the system moves one level at a time to ensure gradual progression.

**Q: What if I fail an expert quiz?**
A: If your score drops below 50%, the system will move you back to hard difficulty.

**Q: Does difficulty_preference affect my statistics?**
A: No, manually selected difficulty is still recorded and contributes to your avg_score.

**Q: Can I reset my difficulty?**
A: Contact administrator or use `POST /progress/reset` to clear performance history.

**Q: Why did difficulty not change even though I scored 85%?**
A: If you're already at "expert" level, there's no higher difficulty to move to.

---

## Support

For issues or questions:
- GitHub Issues: [Report a bug]
- Documentation: `/study/info` endpoint
- Email: support@studyquest.com

---

**Last Updated:** January 2025
**Version:** 1.0
**Author:** StudyQuest Development Team
