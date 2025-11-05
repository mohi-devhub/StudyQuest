# Adaptive Quiz System - Quick Reference

## 🚀 Quick Start

### 1. Generate Adaptive Quiz

```bash
curl -X POST "http://localhost:8000/study/adaptive-quiz" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Machine Learning",
    "num_questions": 5
  }'
```

### 2. Generate with Difficulty Preference

```bash
curl -X POST "http://localhost:8000/study/adaptive-quiz" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python",
    "difficulty_preference": "hard",
    "num_questions": 7
  }'
```

---

## 📊 Difficulty Levels

| Level | When Used | Cognitive Level | Temperature |
|-------|-----------|----------------|-------------|
| **Easy** | avg_score < 50% OR new user needing basics | Recall & Understanding | 0.6 |
| **Medium** | 50% ≤ avg_score < 80% OR new users (default) | Application & Analysis | 0.7 |
| **Hard** | avg_score ≥ 80% from medium | Evaluation & Synthesis | 0.8 |
| **Expert** | avg_score ≥ 80% from hard | Problem-Solving & Critical Thinking | 0.85 |

---

## 🎯 Adaptive Logic Thresholds

```python
if avg_score >= 80:  # INCREASE difficulty
    current → current + 1
    
elif avg_score < 50:  # DECREASE difficulty
    current → current - 1
    
else:  # MAINTAIN (50-79%)
    current → current
```

**Boundaries:**
- Cannot go above "expert"
- Cannot go below "easy"
- Moves one level at a time

---

## 📝 Request Schema

```typescript
{
  topic: string;                    // Required: quiz subject
  difficulty_preference?: string;   // Optional: "easy"|"medium"|"hard"|"expert"
  num_questions?: number;           // Optional: default 5
  notes?: string;                   // Optional: custom study material
}
```

---

## 📤 Response Schema

```typescript
{
  topic: string;
  difficulty: string;
  questions: [
    {
      question: string;
      options: { A, B, C, D };
      correct_answer: string;
      explanation: string;
    }
  ];
  adaptive_metadata: {
    user_performance: {
      avg_score: number | null;
      total_attempts: number;
      last_difficulty: string | null;
    };
    recommended_difficulty: string;
    reasoning: string;
    adjusted_from?: string;  // Present if difficulty changed
  };
  model: string;
  cognitive_level: string;
}
```

---

## 🧪 Testing

```bash
# Run all adaptive quiz tests
cd backend
source venv/bin/activate
python3 test_adaptive_quiz.py

# Expected output
✅ ALL TESTS PASSED (7/7)
```

---

## 🔄 Integration Flow

```
1. User requests quiz
   ↓
2. System fetches performance from Supabase
   ├─> progress.avg_score
   ├─> progress.total_attempts
   └─> xp_logs.metadata.difficulty
   ↓
3. Determine difficulty
   ├─> Check user_preference (if provided)
   ├─> Apply thresholds (80% / 50%)
   └─> Generate reasoning
   ↓
4. Generate quiz with AI
   ├─> Use difficulty-specific temperature
   ├─> Apply cognitive level targeting
   └─> Validate questions
   ↓
5. Return quiz + metadata
   ↓
6. User completes quiz
   ↓
7. Submit to /progress/evaluate
   ├─> Updates avg_score
   ├─> Awards XP (with difficulty bonus)
   └─> Records difficulty in metadata
```

---

## 📁 Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `agents/adaptive_quiz_agent.py` | Core adaptive logic | 450+ |
| `utils/adaptive_quiz_utils.py` | Supabase integration | 250+ |
| `routes/study.py` | API endpoint | Modified |
| `test_adaptive_quiz.py` | Test suite | 400+ |
| `docs/adaptive-quiz-api.md` | Full documentation | 500+ |

---

## ⚙️ Configuration

### Environment Variables

```bash
OPENROUTER_API_KEY=your_key      # Required for AI
SUPABASE_URL=your_url            # Required for tracking
SUPABASE_KEY=your_key            # Required for tracking
```

### Adjustable Thresholds

Edit `adaptive_quiz_agent.py`:

```python
class AdaptiveQuizAgent:
    INCREASE_THRESHOLD = 80  # Change here
    DECREASE_THRESHOLD = 50  # Change here
```

---

## 🎓 Example User Journeys

### New User
```
Quiz 1: No history → defaults to "medium"
Reasoning: "Welcome! Starting at medium difficulty."
```

### High Performer
```
History: avg_score=88%, last="medium", attempts=10
Next Quiz: "hard"
Reasoning: "Your average score of 88.0% shows strong mastery. 
           Ready to challenge yourself at hard level."
```

### Struggling Student
```
History: avg_score=42%, last="hard", attempts=5
Next Quiz: "medium"
Reasoning: "Your average score of 42.0% suggests you need more practice. 
           Trying medium level will help build confidence."
```

---

## 🐛 Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Missing/invalid token | Include `Authorization: Bearer TOKEN` |
| 400 Invalid difficulty | Wrong difficulty value | Use: easy, medium, hard, or expert |
| 400 Empty topic | No topic provided | Include valid `topic` field |
| 500 Generation failure | API key or network issue | Check OPENROUTER_API_KEY, try again |

---

## 📊 Performance Tracking

After quiz completion:

```bash
POST /progress/evaluate
{
  "quiz_type": "adaptive",
  "score": 85,
  "difficulty": "hard",
  "max_score": 100
}
```

**Updates:**
- ✅ avg_score in `progress` table
- ✅ XP points (base + difficulty + performance bonuses)
- ✅ difficulty in `xp_logs.metadata`

**XP Calculation:**
- Base: 100 XP
- Difficulty Bonus: easy=10, medium=20, hard=30, expert=50
- Performance Bonus: perfect=50, excellent=30, good=15, passing=0
- **Range: 110-200 XP**

---

## 🔗 Related Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/study/adaptive-quiz` | POST | Generate adaptive quiz |
| `/progress/evaluate` | POST | Submit quiz results |
| `/progress/{user_id}` | GET | Get user stats |
| `/progress/calculate-xp` | POST | Preview XP for score |
| `/study/info` | GET | API documentation |

---

## 📚 Documentation

- **Quick Reference:** This file
- **Full API Docs:** `docs/adaptive-quiz-api.md`
- **Implementation Guide:** `docs/ADAPTIVE_QUIZ_IMPLEMENTATION.md`
- **XP System:** `docs/xp-calculation-logic.md`

---

## ✅ Feature Checklist

- [x] Automatic difficulty adjustment
- [x] 4 difficulty levels (easy → expert)
- [x] Performance thresholds (80% / 50%)
- [x] Temperature-based generation
- [x] Cognitive level targeting
- [x] User preference override
- [x] Supabase integration
- [x] Detailed reasoning
- [x] New user support
- [x] XP bonus integration
- [x] Comprehensive testing
- [x] Complete documentation

---

## 🚀 Status

**Version:** 1.0  
**Test Status:** ✅ ALL 7 TESTS PASSING  
**Production Ready:** YES

---

**Need Help?**
- View full docs: `docs/adaptive-quiz-api.md`
- Run tests: `python3 test_adaptive_quiz.py`
- Check API: `GET /study/info`
