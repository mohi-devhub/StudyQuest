# 🔄 Frontend Migration Guide - Remove Hardcoded demo_user

## Overview
This guide shows how to update all frontend pages to use the `useAuth` hook instead of hardcoded `'demo_user'`.

---

## ✅ Already Updated
- ✅ `app/study/page.tsx` - Uses `userId` from useAuth

---

## 🔧 Files That Need Updates

### 1. `app/page.tsx` (Dashboard)

**Current:**
```typescript
userId: 'demo_user',
```

**Update to:**
```typescript
import { useAuth } from '@/lib/useAuth'

export default function Dashboard() {
  const { userId } = useAuth()
  
  // Replace line 158:
  userId: userId,  // or just: userId,
  
  // Replace line 215:
  user_id: userId,
}
```

---

### 2. `app/quiz/result/page.tsx`

**Current:**
```typescript
user_id: 'demo_user',
```

**Update to:**
```typescript
import { useAuth } from '@/lib/useAuth'

export default function QuizResultPage() {
  const { userId } = useAuth()
  
  // Replace line 95:
  user_id: userId,
}
```

---

### 3. `app/progress/page.tsx`

**Current:**
```typescript
const userId = 'demo_user'
username: 'demo_user'
<CoachFeedbackPanel userId="demo_user" />
```

**Update to:**
```typescript
import { useAuth } from '@/lib/useAuth'

export default function ProgressPage() {
  const { userId, user } = useAuth()
  
  // Replace line 50:
  const userId = useAuth().userId  // Remove this line
  
  // Replace line 64:
  username: user?.user_metadata?.username || userId
  
  // Replace line 274:
  <CoachFeedbackPanel userId={userId} />
  
  // Lines 206, 392 are just UI display - can keep as examples
}
```

---

### 4. `app/achievements/page.tsx`

**Current:**
```typescript
const userId = 'demo_user' // In production, get from auth
```

**Update to:**
```typescript
import { useAuth } from '@/lib/useAuth'

export default function AchievementsPage() {
  const { userId } = useAuth()
  
  // Replace line 36:
  const { userId } = useAuth()  // Remove the comment
  
  // Line 289 is just terminal command example - can keep
}
```

---

### 5. `app/leaderboard/page.tsx`

**Current:**
```typescript
${entry.id === 'demo_user' ? 'bg-opacity-95' : ''}
{entry.id === 'demo_user' && (
```

**Update to:**
```typescript
import { useAuth } from '@/lib/useAuth'

export default function LeaderboardPage() {
  const { userId } = useAuth()
  
  // Replace line 208:
  ${entry.id === userId ? 'bg-opacity-95' : ''}
  
  // Replace line 224:
  {entry.id === userId && (
}
```

---

## 📋 Quick Migration Checklist

For each page:

1. **Import useAuth:**
   ```typescript
   import { useAuth } from '@/lib/useAuth'
   ```

2. **Get userId in component:**
   ```typescript
   export default function MyPage() {
     const { userId, user, loading } = useAuth()
   ```

3. **Replace all `'demo_user'` with `userId`:**
   - Search: `'demo_user'`
   - Replace: `userId`
   - Except: UI examples/terminal commands

4. **Handle loading state (optional):**
   ```typescript
   if (loading) {
     return <div>Loading...</div>
   }
   ```

5. **Test the page:**
   - Verify it works with demo_user
   - Verify it works with real auth

---

## 🧪 Testing Each Page

### Dashboard (`app/page.tsx`)
```bash
# Should work without errors
npm run dev
# Visit http://localhost:3000
# Check browser console for errors
```

### Quiz Result (`app/quiz/result/page.tsx`)
```bash
# Complete a quiz first
# Visit results page
# Should show XP without errors
```

### Progress (`app/progress/page.tsx`)
```bash
# Visit http://localhost:3000/progress
# Should load user progress
# Coach feedback should work
```

### Achievements (`app/achievements/page.tsx`)
```bash
# Visit http://localhost:3000/achievements
# Should load badges
# No console errors
```

### Leaderboard (`app/leaderboard/page.tsx`)
```bash
# Visit http://localhost:3000/leaderboard
# Your entry should be highlighted
# No console errors
```

---

## 🎯 Expected Behavior

### With `demo_user` (default):
- All pages work as before
- userId = 'demo_user'
- No authentication required

### With Real Auth:
- Pages use real user ID from JWT
- Data is isolated per user
- RLS policies enforce security

---

## 🚨 Common Issues

### Issue: "useAuth must be used within an AuthProvider"
**Solution:** Make sure `app/layout.tsx` has `<AuthProvider>` wrapper

### Issue: "userId is null"
**Solution:** Check that Supabase client is configured in `lib/supabase.ts`

### Issue: "demo_user still appearing"
**Solution:** Search for remaining `'demo_user'` strings (except UI examples)

---

## 📝 Complete Example

Here's a full example for `app/page.tsx`:

```typescript
'use client'

import { useAuth } from '@/lib/useAuth'
import { useState, useEffect } from 'react'

export default function Dashboard() {
  const { userId, user, loading } = useAuth()
  const [data, setData] = useState(null)
  
  useEffect(() => {
    if (!userId) return
    
    // Fetch dashboard data for authenticated user
    fetchDashboardData(userId)
  }, [userId])
  
  const fetchDashboardData = async (userId: string) => {
    const response = await fetch(`${API_URL}/dashboard`, {
      headers: {
        'Authorization': `Bearer ${user?.access_token}`  // Optional: Add token
      }
    })
    const data = await response.json()
    setData(data)
  }
  
  if (loading) {
    return <div className="min-h-screen bg-black text-white p-8">
      <div>Loading...</div>
    </div>
  }
  
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <h1>Welcome, {user?.user_metadata?.username || userId}</h1>
      {/* Rest of dashboard */}
    </div>
  )
}
```

---

## ✅ Verification

After updating all files:

1. **Search for remaining demo_user:**
   ```bash
   cd frontend
   grep -r "demo_user" app/
   ```
   
   Should only show:
   - Comments
   - Terminal command examples
   - UI display text

2. **Run frontend:**
   ```bash
   npm run dev
   ```
   
3. **Test all pages:**
   - Dashboard: http://localhost:3000
   - Study: http://localhost:3000/study
   - Quiz: http://localhost:3000/quiz
   - Progress: http://localhost:3000/progress
   - Achievements: http://localhost:3000/achievements
   - Leaderboard: http://localhost:3000/leaderboard

4. **Check console:**
   - No errors about undefined userId
   - No auth errors
   - API calls succeed

---

## 🎉 Success Criteria

All pages should:
- ✅ Use `useAuth` hook
- ✅ Get `userId` dynamically
- ✅ Work with demo_user (default)
- ✅ Ready for real auth
- ✅ No hardcoded user IDs in API calls
- ✅ No console errors

---

**Status:** In Progress  
**Completed:** 1/6 pages (study page)  
**Remaining:** 5 pages (dashboard, quiz result, progress, achievements, leaderboard)

**Estimated Time:** 30 minutes to update all pages

---

**Next Steps:**
1. Update `app/page.tsx`
2. Update `app/quiz/result/page.tsx`
3. Update `app/progress/page.tsx`
4. Update `app/achievements/page.tsx`
5. Update `app/leaderboard/page.tsx`
6. Test everything
7. Deploy to production
