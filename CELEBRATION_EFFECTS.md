# Achievement Celebration Effects

## Overview

Lightweight, text-based celebration effects for achievements using ASCII art, animations, and monochrome design.

## Components

### 1. CelebrationModal
**Location:** `frontend/components/CelebrationModal.tsx`

Full-screen modal for major achievements (level ups, badge unlocks).

**Features:**
- ✅ ASCII border decorations (`────────`)
- ✅ Typewriter effect for title text
- ✅ Framer Motion animations (fade + slide)
- ✅ Auto-dismisses after 5 seconds
- ✅ Click anywhere to close
- ✅ Symbol display for badges
- ✅ Monochrome only (black & white)

**Usage:**
```tsx
<CelebrationModal
  type="level"  // 'level' | 'badge'
  title="🎉 LEVEL UP!"
  message="You are now Level 6 – Curious Mind"
  symbol="[★★]"  // Optional, for badges
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
/>
```

**Example Output:**
```
────────────────────────────────────────
                [★★]

        🎉 LEVEL UP!
        
You are now Level 6 – Curious Mind

────────────────────────────────────────
     Click anywhere to dismiss
```

---

### 2. InlineCelebration
**Location:** `frontend/components/InlineCelebration.tsx`

Smaller inline celebration for quiz completions and minor achievements.

**Features:**
- ✅ Animated borders (width expansion)
- ✅ Rotating symbol entrance
- ✅ Fade-in message
- ✅ Lightweight, non-intrusive
- ✅ Pure monochrome

**Usage:**
```tsx
<InlineCelebration 
  message="EXCELLENT WORK!"
  symbol="★★★"
/>
```

**Example Output:**
```
─────────────────────
        ★★★
   EXCELLENT WORK!
─────────────────────
```

---

## Integration Points

### Dashboard (Level Up)
**File:** `frontend/app/page.tsx`

```tsx
const handleLevelUp = useCallback((newLevel: number) => {
  setCelebration({
    isOpen: true,
    type: 'level',
    title: `🎉 LEVEL UP!`,
    message: `You are now Level ${newLevel} – Curious Mind`,
  })
}, [])
```

### Dashboard (Badge Unlock)
**File:** `frontend/app/page.tsx`

```tsx
const handleBadgeUnlock = useCallback((badge: any) => {
  setCelebration({
    isOpen: true,
    type: 'badge',
    title: `🏆 BADGE UNLOCKED!`,
    message: badge.description,
    symbol: badge.symbol,
  })
}, [])
```

### Quiz Results (High Score)
**File:** `frontend/app/quiz/result/page.tsx`

```tsx
{result.score >= 70 && (
  <InlineCelebration 
    message={result.score >= 90 ? '🎉 EXCELLENT WORK!' : '✓ GREAT JOB!'}
    symbol={result.score >= 90 ? '★★★' : '★★'}
  />
)}
```

---

## Real-Time Badge Notifications

### useRealtimeXP Hook
**File:** `frontend/lib/useRealtimeXP.ts`

**New Feature:** Badge unlock listener

```typescript
const badgeChannel = supabase
  .channel('public:user_badges')
  .on('postgres_changes', 
    { event: 'INSERT', table: 'user_badges', filter: `user_id=eq.${userId}` },
    async (payload) => {
      // Fetch badge details and trigger celebration
      onBadgeUnlock(badgeData)
    }
  )
```

**Required Props:**
```typescript
interface UseRealtimeXPProps {
  userId: string
  onXPGain?: (points: number, reason: string, topic?: string) => void
  onLevelUp?: (newLevel: number) => void
  onProgressUpdate?: (topic: string, avgScore: number) => void
  onBadgeUnlock?: (badge: UnlockedBadge) => void  // NEW
}
```

---

## Level Titles

Predefined titles for milestone levels:

| Level | Title              |
|-------|-------------------|
| 5     | Novice Scholar    |
| 10    | Curious Mind      |
| 15    | Dedicated Learner |
| 20    | Knowledge Seeker  |
| 25    | Wise Student      |
| 30    | Sage              |

**Usage in Code:**
```typescript
const levelTitles: { [key: number]: string } = {
  5: 'Novice Scholar',
  10: 'Curious Mind',
  20: 'Knowledge Seeker',
  30: 'Sage',
}

const title = levelTitles[newLevel] || 'Knowledge Seeker'
```

---

## Animation Details

### CelebrationModal Animations

1. **Entrance:**
   - Backdrop: Fade in (opacity 0 → 1)
   - Modal: Slide up + scale (y: -50 → 0, scale: 0.9 → 1)
   - Spring physics: damping=20, stiffness=300

2. **Symbol (Badge):**
   - Rotate entrance: -180° → 0°
   - Scale: 0 → 1
   - Spring: damping=10, stiffness=100
   - Delay: 200ms

3. **Title (Typewriter):**
   - Character-by-character reveal
   - Speed: 50ms per character
   - Blinking cursor while typing

4. **Message:**
   - Fade in + slide up
   - Delay: After typewriter completes

5. **Exit:**
   - Slide down + fade out
   - Scale down to 0.9

### InlineCelebration Animations

1. **Container:** Scale up (0.8 → 1) + fade in
2. **Borders:** Width expansion (0% → 100%)
3. **Symbol:** Rotate (-180° → 0°) + scale (0 → 1)
4. **Message:** Fade in + slide up

---

## Design Principles

### ✅ Monochrome Only
- White text on black background
- No color gradients
- Gray borders (`#CCCCCC`, `#808080`)

### ✅ ASCII Symbols
- Borders: `─` (horizontal line)
- Stars: `★` (for ratings)
- Brackets: `[ ]` (for badge symbols)
- Arrows: `▸` (for progression)

### ✅ Typography
- Font: JetBrains Mono (monospace)
- Tracking: Wider for titles
- Weight contrast: Bold for emphasis

### ✅ Timing
- Auto-dismiss: 5 seconds
- Typewriter speed: 50ms/char
- Animation delays: Staggered (100-500ms)

---

## Testing

### Trigger Level Up (SQL)
```sql
-- Set user to level threshold
UPDATE users 
SET total_xp = 4999 
WHERE user_id = 'demo_user';

-- Trigger level up
UPDATE users 
SET total_xp = 5000,
    level = 10
WHERE user_id = 'demo_user';
```

**Expected:** CelebrationModal appears with "LEVEL UP! Level 10 – Curious Mind"

### Trigger Badge Unlock (SQL)
```sql
-- Manually award a badge
INSERT INTO user_badges (user_id, badge_id, seen)
SELECT 'demo_user', id, false
FROM badges
WHERE badge_key = 'curious_mind'
ON CONFLICT (user_id, badge_id) DO NOTHING;
```

**Expected:** CelebrationModal appears with badge symbol and description

### Test Quiz Celebration
1. Complete any quiz with score ≥ 70%
2. Navigate to quiz results page
3. **Expected:** InlineCelebration appears between quiz info and score

---

## Performance

### Optimizations

1. **GPU Acceleration:**
   - All animations use `transform` and `opacity`
   - No layout thrashing

2. **Lazy Loading:**
   - Components only rendered when needed
   - Auto-cleanup on unmount

3. **Debouncing:**
   - Auto-dismiss timers properly cleared
   - No memory leaks

4. **Bundle Size:**
   - CelebrationModal: ~2KB gzipped
   - InlineCelebration: ~1KB gzipped
   - Total: ~3KB additional

---

## Accessibility

- ✅ Click anywhere to dismiss (easy exit)
- ✅ Auto-dismiss after 5s (no user action required)
- ✅ High contrast (black & white)
- ✅ Large text (2xl-3xl font sizes)
- ⚠️ TODO: Add keyboard support (ESC to close)
- ⚠️ TODO: Add ARIA labels

---

## Future Enhancements

### Planned Features

1. **Sound Effects** (Optional, user-controlled)
   - Subtle "ding" for badge unlock
   - Whoosh for level up
   - Muted by default

2. **Confetti ASCII Animation**
   ```
   *  .  *    .   *
     .   *  .   *
   *   .    *  .
   ```

3. **Streak Celebrations**
   - Daily login streaks
   - Perfect quiz streaks
   - Topic mastery streaks

4. **Milestone Messages**
   - "First quiz completed!"
   - "10 badges earned!"
   - "100 quizzes completed!"

5. **Customization**
   - User preference: Enable/disable celebrations
   - Animation speed control
   - Symbol preferences

---

## File Structure

```
frontend/
├── components/
│   ├── CelebrationModal.tsx       # Full-screen celebration
│   ├── InlineCelebration.tsx      # Inline mini-celebration
│   └── Toast.tsx                  # Existing toast system
├── lib/
│   └── useRealtimeXP.ts           # Real-time badge listener
├── app/
│   ├── page.tsx                   # Dashboard integration
│   └── quiz/result/page.tsx       # Quiz result integration
└── app/globals.css                # Monochrome theme styles
```

---

## Dependencies

### Required Packages
- `framer-motion` - Animations
- `react` - Component framework
- `@supabase/supabase-js` - Real-time subscriptions

### Peer Dependencies
- Next.js 14+
- TypeScript 5+
- Tailwind CSS 3+

---

## Migration Notes

### Breaking Changes
- None (pure addition)

### Database Requirements
- `user_badges` table must have real-time enabled
- Foreign key: `badges.id` → `user_badges.badge_id`

### Environment Variables
- No additional variables required
- Uses existing `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`

---

## Credits

**Design:** Monochrome terminal aesthetic  
**Animations:** Framer Motion v11  
**Typography:** JetBrains Mono  
**Real-time:** Supabase Realtime  

**Commit:** `feat: Add subtle text-based celebration for achievements`  
**Date:** November 6, 2025  
**Version:** 1.1.0
