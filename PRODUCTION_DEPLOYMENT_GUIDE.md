# 🚀 Production Deployment Guide - Removing Demo User

## Overview
This guide explains how to transition from demo_user testing mode to production with real authentication.

---

## 📋 Pre-Production Checklist

Before removing demo_user support, ensure:

### Backend
- [ ] All endpoints use `Depends(verify_user)` 
- [ ] No hardcoded `'demo_user'` in route handlers
- [ ] Environment variables set for production
- [ ] Rate limiting configured
- [ ] CORS set to production domain only

### Frontend  
- [ ] All pages use `useAuth()` hook
- [ ] No hardcoded `'demo_user'` in API calls
- [ ] Login/signup pages functional
- [ ] Protected routes have auth guards
- [ ] Session persistence working

### Database
- [ ] Test users created in Supabase Auth
- [ ] Database backup taken
- [ ] RLS currently working with demo_user

---

## 🔄 Migration Steps

### Step 1: Test Current Setup

```bash
# Verify backend works with demo_user
curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "num_questions": 5}'

# Should work (demo_user has access)
```

### Step 2: Update Backend Code

Remove any remaining hardcoded demo_user:

```bash
# Search for demo_user in backend
cd backend
grep -r "demo_user" routes/ utils/

# Should return NO results (or only comments)
```

### Step 3: Update Frontend Code

Follow `FRONTEND_MIGRATION_GUIDE.md` to update remaining pages:

- [ ] `app/page.tsx` (Dashboard)
- [ ] `app/quiz/result/page.tsx`
- [ ] `app/progress/page.tsx`
- [ ] `app/achievements/page.tsx`
- [ ] `app/leaderboard/page.tsx`

**Quick update:**
```typescript
// Find and replace in each file:
// Old: user_id: 'demo_user'
// New: user_id: userId  (from useAuth hook)

import { useAuth } from '@/lib/useAuth'

export default function MyPage() {
  const { userId } = useAuth()
  
  // Use userId in API calls
}
```

### Step 4: Update Environment Variables

```bash
# backend/.env (Production)
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-domain.vercel.app
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key  # ⚠️ ANON key, not service role
OPENROUTER_API_KEY=your_api_key
```

### Step 5: Run Production RLS Migration

**Option A: Use the production migration file**
```sql
-- In Supabase SQL Editor
-- Copy/paste: migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql
-- Click RUN
```

**Option B: Modify existing migration**
```sql
-- Open: migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql
-- Find: user_id = 'demo_user' OR 
-- Replace with: (empty)
-- Save and run in Supabase
```

### Step 6: Verify RLS Policies

```sql
-- Check policies no longer have demo_user
SELECT 
  tablename,
  policyname,
  definition
FROM pg_policies
WHERE schemaname = 'public'
  AND definition LIKE '%demo_user%';

-- Should return: 0 rows
```

### Step 7: Test Authentication

**Create a test user:**
```bash
# In Supabase Dashboard -> Authentication -> Users
# Or via signup API:
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "username": "testuser"
  }'
```

**Test login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'

# Should return: JWT token
```

**Test protected endpoint:**
```bash
# Get token from login response
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/quiz \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"topic": "Python", "num_questions": 5}'

# Should return: Quiz data
```

### Step 8: Test RLS Enforcement

```sql
-- As authenticated user (via JWT)
-- Should see own data only
SELECT * FROM progress WHERE user_id = auth.uid()::text;

-- Try to access other user's data
SELECT * FROM progress WHERE user_id = 'different_user_id';
-- Should return: 0 rows (RLS blocks it)
```

### Step 9: Deploy Backend

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Test locally first
uvicorn main:app --host 0.0.0.0 --port 8000

# Deploy to your hosting platform
# (Railway, Render, AWS, etc.)
```

### Step 10: Deploy Frontend

```bash
cd frontend
npm install
npm run build

# Test production build locally
npm run start

# Deploy to Vercel
vercel --prod
```

---

## 🧪 Post-Deployment Testing

### 1. Test Unauthenticated Access (Should Fail)

```bash
# Try to access protected endpoint without auth
curl -X POST https://your-api.com/quiz \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python"}'

# Expected: 401 Unauthorized
```

### 2. Test Authenticated Access (Should Work)

```bash
# 1. Sign up
curl -X POST https://your-api.com/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Pass123!", "username": "user"}'

# 2. Login
curl -X POST https://your-api.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Pass123!"}'

# 3. Use returned token
TOKEN="<token_from_login>"
curl -X POST https://your-api.com/quiz \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python"}'

# Expected: 200 OK with quiz data
```

### 3. Test Data Isolation

```sql
-- In Supabase SQL Editor
-- Create two test users
INSERT INTO users (user_id, username, email)
VALUES 
  ('user1', 'User One', 'user1@test.com'),
  ('user2', 'User Two', 'user2@test.com');

-- Add progress for user1
INSERT INTO progress (user_id, topic, avg_score)
VALUES ('user1', 'Python', 85);

-- Try to view as user2 (should be blocked by RLS)
-- This would require setting session to user2's auth
SET request.jwt.claim.sub = 'user2';
SELECT * FROM progress WHERE user_id = 'user1';
-- Returns: 0 rows (RLS blocks cross-user access)
```

### 4. Test Frontend Auth Flow

1. **Visit your site:** https://your-domain.vercel.app
2. **Try to access protected page** (e.g., /progress)
3. **Should redirect to login** (if middleware configured)
4. **Sign up as new user**
5. **Verify email** (if enabled)
6. **Login successfully**
7. **Access protected pages** (should work)
8. **Submit quiz** (should save with real user_id)
9. **Check leaderboard** (should show real users, not demo_user)

---

## ⚠️ Troubleshooting

### Issue: "401 Unauthorized" on all requests

**Cause:** JWT token not being sent or invalid

**Fix:**
```typescript
// Ensure frontend sends token
const { user } = useAuth()
const token = await user?.getIdToken()

fetch(API_URL, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

### Issue: "RLS policy violation"

**Cause:** Backend using service role key instead of user JWT

**Fix:**
```python
# backend/config/supabase_client.py
# Make sure you're using ANON key, not service role
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Should be anon key

# Or create client with user JWT
from utils.auth import get_user_supabase_client
user_supabase = get_user_supabase_client(user_token)
```

### Issue: "demo_user" still appearing in database

**Cause:** Old data or frontend still using hardcoded value

**Fix:**
```sql
-- Clean up old demo_user data
DELETE FROM progress WHERE user_id = 'demo_user';
DELETE FROM quiz_scores WHERE user_id = 'demo_user';
DELETE FROM users WHERE user_id = 'demo_user';
```

```bash
# Search frontend for remaining demo_user
cd frontend
grep -r "demo_user" app/

# Should only show comments/examples
```

---

## 🔄 Rollback Plan

If something goes wrong:

### Rollback RLS Policies

```sql
-- Re-run the demo mode migration
-- migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql
-- This adds demo_user support back
```

### Rollback Environment

```bash
# backend/.env
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Restore Database

```bash
# In Supabase Dashboard
# Database -> Backups -> Select backup -> Restore
```

---

## ✅ Production Checklist

Final verification before going live:

### Security
- [ ] No demo_user in RLS policies
- [ ] No hardcoded credentials in code
- [ ] HTTPS enforced (ENVIRONMENT=production)
- [ ] Rate limiting active
- [ ] CORS set to production domain only
- [ ] Security headers present in responses

### Authentication
- [ ] Supabase Auth configured
- [ ] Email verification enabled (recommended)
- [ ] Password requirements enforced
- [ ] JWT tokens working
- [ ] Session persistence working

### Backend
- [ ] All endpoints require auth (except public)
- [ ] Environment variables set
- [ ] Dependencies up to date
- [ ] Logs configured
- [ ] Error monitoring setup (Sentry)

### Frontend
- [ ] All pages use useAuth
- [ ] Login/signup working
- [ ] Protected routes guarded
- [ ] Loading states handled
- [ ] Error boundaries in place

### Database
- [ ] RLS policies enforced
- [ ] Indexes optimized
- [ ] Backups automated
- [ ] demo_user data cleaned up

### Testing
- [ ] Signup flow tested
- [ ] Login flow tested
- [ ] Quiz submission tested
- [ ] Progress tracking tested
- [ ] Leaderboard shows real users
- [ ] Data isolation verified

---

## 📊 Comparison: Before vs After

| Feature | With demo_user | Production (No demo_user) |
|---------|---------------|---------------------------|
| **Authentication** | Optional | Required |
| **RLS Policies** | `demo_user OR auth.uid()` | `auth.uid()` only |
| **Data Access** | Anyone can use demo_user | Only own data |
| **Security Level** | Testing (6/10) | Production (9/10) |
| **User Isolation** | Partial | Complete |

---

## 🎯 Success Criteria

Your app is ready for production when:

1. ✅ No demo_user in any RLS policies
2. ✅ All API requests require authentication
3. ✅ Users can only access their own data
4. ✅ Signup and login flows work perfectly
5. ✅ Rate limiting prevents abuse
6. ✅ Security headers present
7. ✅ HTTPS enforced
8. ✅ Database backups automated
9. ✅ Error monitoring active
10. ✅ All tests passing

---

**Status:** Ready for production deployment! 🚀

**Files:**
- `migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql` - Production RLS policies
- `migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql` - Development RLS policies

**Next Step:** Run the production migration and deploy!
