# XP Calculation Logic Documentation

## Overview

The StudyQuest XP (Experience Points) system rewards students based on quiz performance and difficulty level. The calculation uses a tiered system that incentivizes challenging oneself with harder material while rewarding high performance.

## Core Function

### `calculate_xp(score: int, difficulty: str) -> int`

**Location**: `backend/utils/progress_tracker.py` in the `XPTracker` class

**Purpose**: Calculate XP points based on quiz score and difficulty level.

**Parameters**:
- `score` (int): Quiz score as percentage (0-100)
- `difficulty` (str): Difficulty level - 'easy', 'medium', 'hard', or 'expert'

**Returns**: Total XP points (int)

## XP Components

The total XP is calculated from three components:

### 1. Base XP (Constant)
- **Value**: 100 points
- **Purpose**: Reward for completing any quiz
- **Logic**: Every student gets this regardless of score or difficulty

### 2. Difficulty Bonus

Rewards students for challenging themselves with harder material.

| Difficulty | Bonus | Description |
|------------|-------|-------------|
| `easy` | +10 XP | Beginner-friendly content |
| `medium` | +20 XP | Standard difficulty (default) |
| `hard` | +30 XP | Advanced material |
| `expert` | +50 XP | Expert-level challenges |

**Logic**: Higher difficulty = higher reward

### 3. Performance Tier Bonus

Rewards students based on quiz score performance.

| Tier | Score Range | Bonus | Description |
|------|-------------|-------|-------------|
| **Perfect** | 100% | +50 XP | Flawless execution |
| **Excellent** | 90-99% | +30 XP | Outstanding performance |
| **Good** | 80-89% | +15 XP | Solid understanding |
| **Passing** | 70-79% | +0 XP | Meets minimum requirement |
| **Below Passing** | 0-69% | +0 XP | Needs improvement |

**Logic**: Higher scores = higher rewards

## Calculation Formula

```python
total_xp = BASE_XP + DIFFICULTY_BONUS + PERFORMANCE_BONUS

# Example: 85% score on hard difficulty
total_xp = 100 + 30 + 15 = 145 XP
```

## Examples

### Example 1: Perfect Score on Expert
```python
score = 100
difficulty = 'expert'

base = 100
difficulty_bonus = 50  # expert
performance_bonus = 50  # perfect (100%)

total_xp = 200
```

### Example 2: Good Score on Medium
```python
score = 85
difficulty = 'medium'

base = 100
difficulty_bonus = 20  # medium
performance_bonus = 15  # good (80-89%)

total_xp = 135
```

### Example 3: Passing Score on Easy
```python
score = 70
difficulty = 'easy'

base = 100
difficulty_bonus = 10  # easy
performance_bonus = 0  # passing (70-79%)

total_xp = 110
```

## XP Ranges

### By Difficulty Level

| Difficulty | Minimum XP (0%) | Maximum XP (100%) | Range |
|------------|-----------------|-------------------|-------|
| Easy | 110 | 160 | 50 |
| Medium | 120 | 170 | 50 |
| Hard | 130 | 180 | 50 |
| Expert | 150 | 200 | 50 |

### Comparison Table

For the same score, XP increases with difficulty:

| Score | Easy | Medium | Hard | Expert |
|-------|------|--------|------|--------|
| 100% | 160 | 170 | 180 | 200 |
| 90% | 140 | 150 | 160 | 180 |
| 80% | 125 | 135 | 145 | 165 |
| 70% | 110 | 120 | 130 | 150 |

**Key Insight**: Challenging yourself with harder material yields more XP!

## API Usage

### Calculate XP Preview (Frontend)

Before submitting quiz answers, show students how much XP they'll earn:

```bash
POST /progress/calculate-xp
Content-Type: application/json

{
  "score": 85,
  "difficulty": "hard"
}
```

**Response**:
```json
{
  "score": 85,
  "difficulty": "hard",
  "total_xp": 145,
  "breakdown": {
    "base_xp": 100,
    "difficulty_bonus": 30,
    "performance_bonus": 15,
    "score_tier": "good"
  },
  "message": "Score of 85% on hard difficulty = 145 XP"
}
```

### Quiz Evaluation with XP

When evaluating a quiz, include the difficulty parameter:

```bash
POST /progress/evaluate
Authorization: Bearer <token>
Content-Type: application/json

{
  "study_package": {...},
  "answers": ["A", "B", "C", "D", "A"],
  "difficulty": "hard"
}
```

**Response includes**:
```json
{
  "score_percentage": 80.0,
  "xp_awarded": 145,
  "total_xp": 1250,
  "difficulty": "hard",
  "score_tier": "good",
  ...
}
```

## Code Examples

### Python (Backend)

```python
from utils.progress_tracker import XPTracker

# Simple calculation
xp = XPTracker.calculate_xp(score=85, difficulty='hard')
print(f"XP earned: {xp}")  # Output: 145

# Get difficulty bonus
bonus = XPTracker.get_difficulty_bonus('expert')
print(f"Expert bonus: {bonus}")  # Output: 50

# Get score tier
tier = XPTracker.get_score_tier(92.5)
print(f"Performance tier: {tier}")  # Output: excellent

# Process quiz completion (full workflow)
result = await XPTracker.process_quiz_completion(
    user_id="uuid",
    topic="Neural Networks",
    score=95.0,
    total_questions=5,
    correct_answers=4,
    difficulty="hard"
)
print(f"XP awarded: {result['xp_awarded']['points']}")
print(f"Total XP: {result['total_xp']}")
```

### JavaScript (Frontend)

```javascript
// Calculate XP preview
async function showXPPreview(score, difficulty) {
  const response = await fetch('/progress/calculate-xp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ score, difficulty })
  });
  
  const data = await response.json();
  
  console.log(`You'll earn ${data.total_xp} XP!`);
  console.log(`Breakdown: ${data.breakdown.base_xp} base + ${data.breakdown.difficulty_bonus} difficulty + ${data.breakdown.performance_bonus} performance`);
  
  return data.total_xp;
}

// Use in quiz submission
const xp = await showXPPreview(85, 'hard');
document.getElementById('xp-preview').textContent = `${xp} XP`;
```

## Helper Functions

### `get_difficulty_bonus(difficulty: str) -> int`

Returns the XP bonus for a specific difficulty level.

```python
bonus = XPTracker.get_difficulty_bonus('hard')  # Returns: 30
```

### `get_score_tier(score: float) -> str`

Determines the performance tier based on score.

```python
tier = XPTracker.get_score_tier(95.0)  # Returns: 'excellent'
```

## Special Bonuses

In addition to the base calculation, the system includes special bonuses:

### First Topic Bonus
- **Value**: +150 XP
- **When**: First quiz ever completed by a user
- **Purpose**: Encourage engagement for new users

### Topic Completion Bonus  
- **Value**: +200 XP (potential future feature)
- **When**: Average score reaches 70%+ on a topic
- **Purpose**: Reward topic mastery

## Gamification Strategy

The XP system is designed to encourage:

1. **Challenge**: Higher difficulty = more XP
2. **Mastery**: Higher scores = more XP
3. **Consistency**: Base XP ensures all efforts are rewarded
4. **Progress**: Tiered bonuses create clear goals (aim for 80%, 90%, 100%)
5. **Engagement**: Special bonuses for milestones

## Testing

Run the comprehensive test suite:

```bash
cd backend
source venv/bin/activate
python3 test_xp_calculation.py
```

**Test Coverage**:
- ✅ All difficulty levels
- ✅ All score tiers
- ✅ Edge cases (0%, 100%, invalid difficulty)
- ✅ Helper functions
- ✅ Real-world scenarios

## Frontend Integration Tips

### 1. Show XP Preview
Before quiz submission, calculate and display potential XP:

```javascript
// While user is taking quiz
const currentScore = calculateCurrentScore();
const xpPreview = await fetch('/progress/calculate-xp', {
  method: 'POST',
  body: JSON.stringify({
    score: currentScore,
    difficulty: selectedDifficulty
  })
});
```

### 2. Difficulty Selector
Let users choose difficulty before starting:

```html
<select id="difficulty">
  <option value="easy">Easy (+10 XP)</option>
  <option value="medium" selected>Medium (+20 XP)</option>
  <option value="hard">Hard (+30 XP)</option>
  <option value="expert">Expert (+50 XP)</option>
</select>
```

### 3. XP Celebration
Animate XP gains after quiz:

```javascript
function celebrateXP(xpAwarded, scoreTier) {
  const messages = {
    'perfect': '🎉 PERFECT! ',
    'excellent': '⭐ EXCELLENT! ',
    'good': '👍 GOOD JOB! ',
    'passing': '✅ PASSED! '
  };
  
  showAnimation(`${messages[scoreTier]}+${xpAwarded} XP`);
}
```

### 4. Progress Bar
Show how close to next tier:

```javascript
// Show how many more points needed for next tier
if (score >= 80 && score < 90) {
  const pointsNeeded = 90 - score;
  showMessage(`${pointsNeeded}% to Excellent tier (+15 more XP!)`);
}
```

## Configuration

To modify XP values, edit `backend/utils/progress_tracker.py`:

```python
class XPTracker:
    # Base XP
    XP_VALUES = {
        'quiz_completed': 100,  # Adjust base XP
        ...
    }
    
    # Difficulty bonuses
    DIFFICULTY_BONUSES = {
        'easy': 10,    # Adjust difficulty rewards
        'medium': 20,
        'hard': 30,
        'expert': 50
    }
    
    # Score tier bonuses
    SCORE_TIER_BONUSES = {
        'perfect': 50,    # Adjust performance rewards
        'excellent': 30,
        'good': 15,
        'passing': 0
    }
```

## Best Practices

1. **Always include difficulty**: Default is 'medium' if not specified
2. **Validate input**: Scores are clamped to 0-100 range
3. **Show breakdowns**: Users like seeing how XP is calculated
4. **Celebrate milestones**: 100, 500, 1000 XP achievements
5. **Be consistent**: Use same difficulty for all questions in a quiz

## FAQs

**Q: Can score be over 100%?**  
A: No, scores are clamped to 100%. Bonus questions should adjust total questions count.

**Q: What happens with invalid difficulty?**  
A: Defaults to 'medium' (20 XP bonus).

**Q: Is difficulty case-sensitive?**  
A: No, it's converted to lowercase before processing.

**Q: Can XP be negative?**  
A: No, minimum XP is 110 (base + easy difficulty).

**Q: How is XP stored?**  
A: In the `xp_logs` table with full metadata (score, difficulty, tier, etc.).

## See Also

- **Progress Tracking**: `docs/progress-tracking.md`
- **API Reference**: `docs/progress-api-reference.md`
- **Test Script**: `backend/test_xp_calculation.py`
- **Implementation**: `backend/utils/progress_tracker.py`
