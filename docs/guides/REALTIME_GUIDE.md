
**Last Updated:** November 5, 2025  
**Status:** ✅ Fully Functional

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Real-Time XP Updates](#realtime-xp-updates)
3. [Toast Notifications](#toast-notifications)
4. [Leaderboard](#leaderboard)
5. [Troubleshooting](#troubleshooting)

---

## Overview

The real-time system uses Supabase Realtime to provide live updates for:
- XP gains
- Level ups
- Leaderboard changes
- Topic progress updates

All with terminal-style monochrome UI.

---

## Real-Time XP Updates

### Implementation

**Hook:** `/frontend/lib/useRealtimeXP.ts`

```typescript
import { useRealtimeXP } from '@/lib/useRealtimeXP'

const { isConnected } = useRealtimeXP({
  userId: 'demo_user',
  onXPGain: (xp, source, topic) => {
    showToast(`${topic} completed!`, xp, 'xp')
  },
  onLevelUp: (newLevel) => {
    showToast(`LEVEL UP! Now level ${newLevel}`)
  },
  onProgressUpdate: (topic, newAvgScore) => {
    // Update UI with new score
  }
})
```

### Subscriptions

**1. XP Logs Table**
```typescript
supabase
  .channel('xp_updates')
  .on('postgres_changes', {
    event: 'INSERT',
    schema: 'public',
    table: 'xp_logs',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    // New XP gain detected
    onXPGain?.(payload.new.xp_amount, payload.new.source, payload.new.topic)
  })
  .subscribe()
```

**2. Users Table (Level Changes)**
```typescript
supabase
  .channel('level_updates')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'users',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    if (payload.new.current_level > payload.old.current_level) {
      onLevelUp?.(payload.new.current_level)
    }
  })
  .subscribe()
```

**3. Progress Table (Topic Updates)**
```typescript
supabase
  .channel('progress_updates')
  .on('postgres_changes', {
    event: 'UPDATE',
    schema: 'public',
    table: 'progress',
    filter: `user_id=eq.${userId}`
  }, (payload) => {
    onProgressUpdate?.(payload.new.topic, payload.new.avg_score)
  })
  .subscribe()
```

### Connection Status

```typescript
const [isConnected, setIsConnected] = useState(false)

channel.on('system', { event: 'connected' }, () => {
  setIsConnected(true)
  console.log('🟢 Real-time connected')
})

channel.on('system', { event: 'disconnected' }, () => {
  setIsConnected(false)
  console.log('🔴 Real-time disconnected')
})
```

---

## Toast Notifications

### Component

**File:** `/frontend/components/Toast.tsx`

### Features

- ✅ Monochrome terminal style
- ✅ Auto-dismiss after 2 seconds
- ✅ Animated XP number (scale bounce)
- ✅ Multiple toast stacking
- ✅ Framer Motion animations

### Usage

```typescript
import { showToast } from '@/components/Toast'

// XP gain
showToast('Quiz completed!', 165, 'xp')
// Displays: "+165 XP | Quiz completed!"

// Success message
showToast('Progress saved!', null, 'success')

// Error message
showToast('Failed to load data', null, 'error')

// Info message
showToast('Loading...', null, 'info')
```

### Design

```css
/* Toast container */
background: #000000
border: 2px solid #FFFFFF
padding: 16px
color: #FFFFFF

/* XP number */
font-size: 1.5rem
font-weight: bold
animation: scale-bounce

/* Message */
font-family: 'JetBrains Mono'
color: #CCCCCC
```

### Animation

```typescript
// Entry animation
initial={{ opacity: 0, y: -20 }}
animate={{ opacity: 1, y: 0 }}
exit={{ opacity: 0, y: -20 }}

// XP number bounce
animate={{ scale: [1, 1.2, 1] }}
transition={{ duration: 0.5 }}
```

---

## Leaderboard

### Page

**File:** `/frontend/app/leaderboard/page.tsx`

### Features

- ✅ Real-time updates via Supabase Realtime
- ✅ ASCII-style table borders
- ✅ Pure B/W design
- ✅ Trophy icons for top 3 (👑🥈🥉)
- ✅ Highlight current user
- ✅ Live connection status

### Design

```
┌──────┬────────────────────┬─────────┬───────┐
│ RANK │ USERNAME           │ TOTAL XP│ LEVEL │
├──────┼────────────────────┼─────────┼───────┤
│ 👑#1 │ demo_user [YOU]    │ 10,450  │ LVL21 │
│ 🥈#2 │ CodeMaster3000     │  5,420  │ LVL11 │
│ 🥉#3 │ AlgoWizard         │  4,890  │ LVL10 │
│   #4 │ PyThOnPrO          │  4,250  │ LVL 9 │
│   #5 │ DataNinja42        │  3,870  │ LVL 8 │
└──────┴────────────────────┴─────────┴───────┘
```

### Implementation

```typescript
const { isConnected } = useRealtimeLeaderboard()

// Fetch leaderboard data
const fetchLeaderboard = async () => {
  const { data } = await supabase
    .from('users')
    .select('user_id, username, total_xp, level')
    .order('total_xp', { ascending: false })
    .limit(10)
  
  const rankedData = data.map((user, index) => ({
    ...user,
    rank: index + 1
  }))
  
  setLeaderboard(rankedData)
}

// Real-time subscription
useEffect(() => {
  if (isConnected) {
    fetchLeaderboard()
  }
}, [isConnected])
```

### Rank Icons

```typescript
const getRankIcon = (rank: number): string => {
  switch (rank) {
    case 1: return '👑'
    case 2: return '🥈'
    case 3: return '🥉'
    default: return '  '
  }
}
```

### Styling

```tsx
<div className={`
  ${entry.user_id === 'demo_user' ? 'bg-terminal-white bg-opacity-5' : ''}
  ${entry.rank <= 3 ? 'text-terminal-white font-bold' : 'text-terminal-gray'}
`}>
  {entry.rank <= 3 && getRankIcon(entry.rank)}
  #{entry.rank} {entry.username}
  {entry.user_id === 'demo_user' && (
    <span className="border border-terminal-white px-2 py-1">YOU</span>
  )}
</div>
```

---

## Troubleshooting

### Connection Issues

**Problem:** Real-time not connecting

**Solutions:**

1. **Check Supabase URL and Key**
   ```typescript
   console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
   console.log('Supabase Key length:', process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY?.length)
   ```

2. **Verify Realtime is enabled in Supabase**
   - Go to Database → Replication
   - Enable for tables: `users`, `xp_logs`, `progress`

3. **Check connection status**
   ```typescript
   const { isConnected } = useRealtimeXP({ userId: 'demo_user' })
   console.log('Connected:', isConnected)
   ```

4. **Inspect browser console for errors**
   ```
   Look for: "WebSocket connection failed" or "Realtime error"
   ```

### Updates Not Appearing

**Problem:** Changes not reflecting in real-time

**Solutions:**

1. **Verify table replication**
   ```sql
   -- In Supabase SQL Editor
   SELECT * FROM pg_publication_tables 
   WHERE pubname = 'supabase_realtime';
   ```

2. **Check filters match**
   ```typescript
   // Make sure user_id matches exactly
   filter: `user_id=eq.${userId}`
   ```

3. **Test with direct database change**
   ```sql
   -- Update XP to trigger event
   UPDATE users 
   SET total_xp = total_xp + 100 
   WHERE user_id = 'demo_user';
   ```

4. **Verify subscription is active**
   ```typescript
   const channel = supabase.channel('test')
   console.log('Channel state:', channel.state)
   // Should be: 'joined'
   ```

### Performance Issues

**Problem:** Too many updates causing lag

**Solutions:**

1. **Debounce updates**
   ```typescript
   import { debounce } from 'lodash'
   
   const debouncedUpdate = debounce((data) => {
     setLeaderboard(data)
   }, 500)
   ```

2. **Limit subscription scope**
   ```typescript
   // Only subscribe to relevant data
   .on('postgres_changes', {
     event: 'UPDATE',
     table: 'users',
     filter: `user_id=eq.${userId}` // Not all users
   })
   ```

3. **Unsubscribe on unmount**
   ```typescript
   useEffect(() => {
     const channel = supabase.channel('updates')
     
     return () => {
       channel.unsubscribe()
     }
   }, [])
   ```

### Toast Spam

**Problem:** Too many toasts appearing

**Solutions:**

1. **Limit toast duration**
   ```typescript
   showToast(message, xp, type, 1500) // 1.5s instead of 2s
   ```

2. **Group similar toasts**
   ```typescript
   let lastToast = null
   
   const showToastOnce = (message) => {
     if (lastToast !== message) {
       showToast(message)
       lastToast = message
     }
   }
   ```

3. **Throttle XP gains**
   ```typescript
   import { throttle } from 'lodash'
   
   const throttledToast = throttle((xp) => {
     showToast(`+${xp} XP`, xp, 'xp')
   }, 1000) // Max 1 per second
   ```

### Data Sync Issues

**Problem:** Leaderboard out of sync

**Solutions:**

1. **Manual refresh button**
   ```tsx
   <button onClick={() => fetchLeaderboard()}>
     REFRESH
   </button>
   ```

2. **Periodic polling as fallback**
   ```typescript
   useEffect(() => {
     if (!isConnected) {
       const interval = setInterval(fetchLeaderboard, 30000) // 30s
       return () => clearInterval(interval)
     }
   }, [isConnected])
   ```

3. **Force refetch on visibility change**
   ```typescript
   useEffect(() => {
     const handleVisibilityChange = () => {
       if (document.visibilityState === 'visible') {
         fetchLeaderboard()
       }
     }
     
     document.addEventListener('visibilitychange', handleVisibilityChange)
     return () => document.removeEventListener('visibilitychange', handleVisibilityChange)
   }, [])
   ```

### Console Logging

**Enable debug mode:**

```typescript
// In lib/supabase.ts
export const supabase = createClient(url, key, {
  realtime: {
    params: {
      eventsPerSecond: 10,
      log_level: 'debug' // Enable debug logs
    }
  }
})
```

**Expected logs:**

```
🟢 Real-time connected
[REALTIME] Subscribing to channel: xp_updates
[REALTIME] Subscription successful
[REALTIME] New event: INSERT on xp_logs
[XP] User gained 165 XP from quiz_completion
```

---

## Testing Real-Time Features

### 1. Test XP Updates

```sql
-- In Supabase SQL Editor
INSERT INTO xp_logs (user_id, xp_amount, source, topic)
VALUES ('demo_user', 100, 'quiz_completion', 'Python Programming');

UPDATE users 
SET total_xp = total_xp + 100,
    current_level = FLOOR(total_xp / 500) + 1
WHERE user_id = 'demo_user';
```

**Expected:** Toast appears with "+100 XP"

### 2. Test Level Up

```sql
-- Set XP just below level threshold
UPDATE users 
SET total_xp = 4999 
WHERE user_id = 'demo_user';

-- Trigger level up
UPDATE users 
SET total_xp = 5000,
    current_level = 11
WHERE user_id = 'demo_user';
```

**Expected:** Toast appears with "LEVEL UP! Now level 11"

### 3. Test Leaderboard Updates

```sql
-- Update another user's XP
UPDATE users 
SET total_xp = total_xp + 500 
WHERE user_id = 'user_1';
```

**Expected:** Leaderboard re-sorts automatically

### 4. Test Connection Status

```javascript
// In browser console
// Disconnect internet
// Check connection indicator shows "OFFLINE"

// Reconnect internet
// Check connection indicator shows "LIVE"
```

---

## Performance Metrics

### Target Performance

- ✅ Real-time latency: <500ms
- ✅ Toast animation: <200ms
- ✅ Leaderboard update: <1s
- ✅ Connection recovery: <2s

### Monitoring

```typescript
// In useRealtimeXP hook
const [metrics, setMetrics] = useState({
  lastUpdate: null,
  latency: 0,
  updateCount: 0
})

channel.on('postgres_changes', (payload) => {
  const now = Date.now()
  const latency = now - new Date(payload.commit_timestamp).getTime()
  
  setMetrics(prev => ({
    lastUpdate: now,
    latency,
    updateCount: prev.updateCount + 1
  }))
  
  console.log(`[REALTIME] Latency: ${latency}ms`)
})
```

---

*Last Updated: November 5, 2025*  
*All real-time features operational*
