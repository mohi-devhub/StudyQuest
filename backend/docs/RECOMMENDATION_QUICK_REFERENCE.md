# Recommendation Agent - Quick Reference

## 🚀 Quick Start

### Get Recommendations

```bash
curl -X GET "http://localhost:8000/study/recommendations?max_recommendations=5&include_ai_insights=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Recommendation Categories

| Category | Priority | Criteria | XP Range |
|----------|----------|----------|----------|
| **Weak Areas** | HIGH | Score < 70% | 120-160 XP |
| **Stale Topics** | MEDIUM | Last attempt > 7 days | 150 XP |
| **New Topics** | LOW | Never attempted | 120-150 XP |

---

## 🎯 Priority Logic

```python
# Priority 1: Weak Areas (Immediate Improvement)
if avg_score < 70:
    priority = "high"
    category = "weak_area"
    urgency = "Address gaps in understanding"

# Priority 2: Stale Topics (Knowledge Retention)
elif days_since_last > 7:
    priority = "medium"
    category = "review"
    urgency = "Maintain knowledge retention"

# Priority 3: New Topics (Knowledge Expansion)
else:
    priority = "low"
    category = "new_learning"
    urgency = "Broaden expertise"
```

---

## 💰 XP Estimation

### Formula

```python
base_xp = 150

difficulty_multipliers = {
    'easy': 0.8,    # 120 XP
    'medium': 1.0,  # 150 XP
    'hard': 1.3,    # 195 XP
    'expert': 1.5   # 225 XP
}

if current_score < 70:
    improvement_bonus = (70 - current_score) * 0.5

total_xp = (base_xp * multiplier) + improvement_bonus
```

### Examples

| Scenario | Difficulty | Base | Bonus | Total |
|----------|-----------|------|-------|-------|
| Weak (45%) | easy | 120 | 12.5 | **132** |
| Weak (62%) | medium | 150 | 4 | **154** |
| Good (85%) | hard | 195 | 0 | **195** |
| Expert (90%) | expert | 225 | 0 | **225** |

---

## 📝 Response Schema

```typescript
{
  recommendations: [
    {
      topic: string;
      reason: string;
      priority: "high" | "medium" | "low";
      category: "weak_area" | "review" | "new_learning";
      current_score: number | null;
      recommended_difficulty: "easy" | "medium" | "hard" | "expert";
      estimated_xp_gain: number;
      urgency: string;
    }
  ];
  ai_insights?: {
    motivational_message: string;
    learning_insight: string;
    priority_advice: string;
  };
  overall_stats: {
    total_attempts: number;
    avg_score: number;
    topics_studied: number;
  };
  metadata: {
    ai_enhanced: boolean;
    generated_at: string;
    new_user?: boolean;
  };
}
```

---

## 🔄 Typical Workflows

### Workflow 1: New User Journey

```
1. GET /study/recommendations
   → Returns starter topics (Python, Web Dev)
   ↓
2. POST /study/adaptive-quiz (topic: "Python")
   → Generates easy-level quiz
   ↓
3. Complete quiz, POST /progress/evaluate
   → Updates progress, earns XP
   ↓
4. GET /study/recommendations
   → Now includes personalized recommendations
```

### Workflow 2: Addressing Weak Areas

```
1. GET /study/recommendations
   → Identifies: "Algorithms" (45%, HIGH priority)
   ↓
2. Study recommended topic
   → Easy difficulty suggested
   ↓
3. Complete quizzes, improve score
   → Score increases: 45% → 55% → 68%
   ↓
4. GET /study/recommendations
   → "Algorithms" still weak but improving
   → Priority remains HIGH until >70%
```

### Workflow 3: Maintaining Skills

```
1. GET /study/recommendations
   → "Database Design" (last: 12 days ago, MEDIUM priority)
   ↓
2. Review recommended topic
   → Medium difficulty quiz
   ↓
3. Complete review quiz
   → Refreshes knowledge, earns XP
   ↓
4. GET /study/recommendations
   → "Database Design" no longer stale
   → Moves to lower priority or disappears
```

---

## 🎓 Recommendation Examples

### High Priority - Weak Area

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

**Action:** Study immediately, use easy difficulty

### Medium Priority - Stale Topic

```json
{
  "topic": "Database Design",
  "reason": "Review needed (last attempt: 12 days ago)",
  "priority": "medium",
  "category": "review",
  "current_score": 75.0,
  "recommended_difficulty": "medium",
  "estimated_xp_gain": 150,
  "urgency": "Maintain knowledge retention"
}
```

**Action:** Schedule review session this week

### Low Priority - New Topic

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

**Action:** Explore when current topics mastered

---

## 🧪 Testing

```bash
# Run recommendation tests
cd backend
source venv/bin/activate
python3 test_recommendations.py

# Expected output
✅ ALL 7 TESTS PASSED!
```

---

## ⚙️ Configuration

### Thresholds

```python
WEAK_AREA_THRESHOLD = 70   # Scores below = weak
STALE_DAYS = 7             # Days before stale
BASE_XP_ESTIMATE = 150     # Base XP per quiz
```

### Difficulty Assignment

| Score Range | Difficulty |
|------------|-----------|
| < 50% | easy |
| 50-69% | medium |
| 70-84% | medium |
| 85%+ | hard |

---

## 🐛 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| No recommendations | New user, no progress | Complete first quiz |
| Only weak areas | Struggling in all topics | Focus on one topic at a time |
| All stale | Inactive for long period | Start with favorite topic |
| No AI insights | API key missing | Add GEMINI_API_KEY |

---

## 📊 Performance Levels

| Level | Avg Score | Description |
|-------|-----------|-------------|
| **Beginner** | < 50% | Building fundamentals |
| **Developing** | 50-69% | Making progress |
| **Proficient** | 70-84% | Strong understanding |
| **Expert** | 85%+ | Mastery level |

---

## 🔗 Related Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /study/recommendations` | Get recommendations |
| `POST /study/adaptive-quiz` | Start adaptive quiz |
| `POST /progress/evaluate` | Submit quiz results |
| `GET /progress/{user_id}` | View progress |

---

## ✅ Quick Checklist

**For Students:**
- [ ] Check recommendations after each quiz
- [ ] Address HIGH priority items first
- [ ] Review MEDIUM priority weekly
- [ ] Explore LOW priority when ready
- [ ] Use estimated XP for planning
- [ ] Read AI insights for motivation

**For Developers:**
- [ ] Valid Bearer token in requests
- [ ] SUPABASE credentials configured
- [ ] GEMINI_API_KEY for AI insights
- [ ] Max 5 recommendations default
- [ ] Handle new user case
- [ ] Error handling implemented

---

## 📈 Success Metrics

Track these to measure effectiveness:

- **Weak Area Resolution:** % of weak topics improved to >70%
- **Review Compliance:** % of stale topics reviewed within 7 days
- **XP Accuracy:** Actual XP vs estimated XP correlation
- **Priority Follow-through:** % of high-priority topics completed first
- **User Engagement:** Recommendation view → quiz completion rate

---

## 🚀 Status

**Version:** 1.0  
**Test Status:** ✅ ALL 7 TESTS PASSING  
**Production Ready:** YES

**Files:**
- `agents/recommendation_agent.py` (500+ lines)
- `utils/recommendation_utils.py` (300+ lines)
- `routes/study.py` (modified)
- `test_recommendations.py` (500+ lines)
- `docs/recommendation-agent-api.md` (600+ lines)

**Features:**
- ✅ 3-tier prioritization
- ✅ XP estimation (120-225)
- ✅ AI insights
- ✅ New user support
- ✅ Edge case handling
- ✅ Comprehensive testing

---

**Need Help?**
- View full docs: `docs/recommendation-agent-api.md`
- Run tests: `python3 test_recommendations.py`
- Check implementation: `docs/RECOMMENDATION_AGENT_IMPLEMENTATION.md`
