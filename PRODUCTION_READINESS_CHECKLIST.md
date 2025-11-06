# StudyQuest Production Readiness Checklist

## 📋 Pre-Deployment Checklist

### ✅ Authentication & Security
- [x] Login page created with Supabase Auth
- [x] Signup page with username, email, password
- [x] Middleware protecting all routes except /login, /signup
- [x] useAuth hook removing demo_user fallback
- [x] All pages using authenticated userId
- [x] JWT verification on backend
- [x] Rate limiting implemented (10 req/min)
- [x] CORS configured with explicit whitelist
- [x] Security headers added
- [ ] **ACTION: Create test user in Supabase Auth**
- [ ] **ACTION: Run CREATE_TEST_USER.sql migration**

### ✅ Code Cleanup
- [x] Removed hardcoded 'demo_user' from all frontend pages
- [x] Dashboard fetches real data from API
- [x] Progress page uses authenticated user
- [x] Achievements page uses authenticated user
- [x] Leaderboard highlights current user
- [x] Quiz results use authenticated user
- [x] Study page already using useAuth
- [ ] **ACTION: Search codebase for any remaining 'demo_user' references**

### ✅ Database
- [ ] **ACTION: Run SUPABASE_SCHEMA.sql in Supabase**
- [ ] **ACTION: Choose RLS mode:**
  - For Dev: Run `migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql`
  - For Prod: Run `migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql`
- [ ] **ACTION: Create test user (see instructions below)**
- [ ] **ACTION: Verify RLS policies: `SELECT * FROM pg_policies`**
- [ ] **ACTION (Optional): Run CLEANUP_DEMO_DATA.sql to remove old data**

### ✅ Environment Variables
- [x] backend/.env.example updated with clear instructions
- [x] frontend/.env.local.example updated
- [ ] **ACTION: Copy .env.example to .env in backend/**
- [ ] **ACTION: Copy .env.local.example to .env.local in frontend/**
- [ ] **ACTION: Fill in all values:**
  - SUPABASE_URL
  - SUPABASE_KEY (anon key)
  - OPENROUTER_API_KEY
  - ALLOWED_ORIGINS
  - JWT_SECRET

### ✅ Documentation
- [x] README.md updated with complete overview
- [x] docs/SETUP_GUIDE.md created
- [x] CREATE_TEST_USER.sql documented
- [x] CLEANUP_DEMO_DATA.sql created
- [x] All migration files documented
- [ ] **ACTION: Review docs for accuracy**

---

## 🚀 Step-by-Step Setup Instructions

### 1. Create Test User in Supabase

**Option A: Via Supabase Dashboard**
1. Go to your Supabase project
2. Authentication → Users
3. Click "Invite User" or "Add User"
4. Fill in:
   - Email: `test@studyquest.dev`
   - Password: `testuser123`
5. Click "Create User"
6. Copy the generated User ID (UUID)
7. In Supabase SQL Editor, run:

```sql
-- Replace <USER_ID> with the actual UUID from step 6
INSERT INTO public.users (user_id, username, total_xp, level, created_at, last_active)
VALUES (
  '<USER_ID>',
  'testuser',
  0,
  1,
  NOW(),
  NOW()
);
```

**Option B: Using SQL Script**
1. First create user via Dashboard (steps 1-6 above)
2. Run entire `migrations/CREATE_TEST_USER.sql` file
3. It will auto-insert the user record

### 2. Clean Database (Optional)

If you have old demo_user data:

```sql
-- Run: migrations/CLEANUP_DEMO_DATA.sql
```

This removes all demo_user data and orphaned records.

### 3. Verify Setup

```sql
-- Check test user exists
SELECT * FROM users WHERE username = 'testuser';

-- Check RLS policies are active
SELECT tablename, policyname FROM pg_policies WHERE schemaname = 'public';

-- Should see ~24 policies across 11 tables
```

---

## 🧪 Testing Checklist

### Local Testing (Before Deployment)

#### Backend Tests
```bash
cd backend

# Check Python syntax
python -m py_compile main.py

# Run backend
uvicorn main:app --reload

# Test health endpoint
curl http://localhost:8000/
# Should return: {"status": "healthy", "message": "StudyQuest API is running"}
```

#### Frontend Tests
```bash
cd frontend

# Lint code
npm run lint

# Build production version
npm run build

# Test build
npm run start
```

### Authentication Flow Test
1. [ ] Open http://localhost:3000
2. [ ] Should redirect to /login
3. [ ] Click "AUTO-FILL_CREDENTIALS"
4. [ ] Should login successfully
5. [ ] Should redirect to /dashboard
6. [ ] Dashboard should load without errors
7. [ ] Check browser console - no errors
8. [ ] Test navigation to /progress, /achievements, /leaderboard
9. [ ] Click logout (if implemented)
10. [ ] Should redirect to /login

### Feature Tests
1. [ ] **Study Notes**
   - Go to /study
   - Generate notes on a topic
   - Verify notes display

2. [ ] **Quiz**
   - Take a quiz
   - Submit answers
   - Check XP gain
   - Verify score saved

3. [ ] **Progress Tracking**
   - Go to /progress
   - Verify topics display
   - Check stats are accurate

4. [ ] **Achievements**
   - Go to /achievements
   - Verify badges display
   - Check if any unlocked

5. [ ] **Leaderboard**
   - Go to /leaderboard
   - Verify user appears
   - Check "YOU" label on your entry

### Security Tests
1. [ ] Try accessing /dashboard without login → should redirect
2. [ ] Try accessing API without auth → should get 401
3. [ ] Verify CORS works for localhost:3000
4. [ ] Test rate limiting (make 11 requests rapidly)
5. [ ] Check browser network tab - auth headers present

---

## 📦 Production Deployment

### Pre-Deployment
1. [ ] All tests passing
2. [ ] No console errors
3. [ ] Environment variables ready for production
4. [ ] Database migrations completed
5. [ ] Test user created

### Backend Deployment (Railway/Render)
1. [ ] Connect GitHub repo
2. [ ] Set environment variables:
   ```bash
   SUPABASE_URL=<production_url>
   SUPABASE_KEY=<anon_key>
   OPENROUTER_API_KEY=<your_key>
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ENVIRONMENT=production
   ```
3. [ ] Deploy
4. [ ] Test health endpoint: `https://your-backend.com/`
5. [ ] Save backend URL for frontend

### Frontend Deployment (Vercel)
1. [ ] Connect GitHub repo
2. [ ] Set environment variables:
   ```bash
   NEXT_PUBLIC_SUPABASE_URL=<your_url>
   NEXT_PUBLIC_SUPABASE_ANON_KEY=<your_key>
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```
3. [ ] Deploy
4. [ ] Test deployed app
5. [ ] Update ALLOWED_ORIGINS in backend to include Vercel URL

### Database (Supabase)
1. [ ] Run production RLS migration:
   ```sql
   -- migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql
   ```
2. [ ] Update Auth settings:
   - Site URL: `https://your-frontend.vercel.app`
   - Redirect URLs: `https://your-frontend.vercel.app/**`
3. [ ] Test auth flow on production

### Post-Deployment
1. [ ] Test full user journey
2. [ ] Monitor logs for errors
3. [ ] Check database for proper data isolation
4. [ ] Verify rate limiting works
5. [ ] Test from different browsers/devices

---

## 🐛 Common Issues & Solutions

### "Cannot connect to Supabase"
- Verify SUPABASE_URL and SUPABASE_KEY
- Check network connectivity
- Ensure using ANON key, not service role

### "401 Unauthorized on API calls"
- Check JWT token in browser cookies
- Verify backend auth middleware
- Ensure useAuth hook working

### "RLS policy violation"
- Ensure using ANON key (not service role)
- Verify RLS policies created
- Check user_id matches auth.uid()

### "Login redirect loop"
- Check middleware.ts logic
- Verify useAuth hook returns correct userId
- Clear browser cookies and try again

### "CORS error"
- Update ALLOWED_ORIGINS in backend .env
- Restart backend server
- Check browser network tab for actual origin

### "Rate limit 429 errors"
- Expected behavior (10 req/min)
- Wait 1 minute
- Or adjust in backend/main.py for testing

---

## ✅ Final Production Checklist

Before going live:

### Code
- [ ] No console.log statements in production code
- [ ] No TODO comments left unaddressed
- [ ] All TypeScript errors resolved
- [ ] All Python lint warnings fixed

### Security
- [ ] All environment variables in .env files (not code)
- [ ] .env and .env.local in .gitignore
- [ ] No API keys in version control
- [ ] RLS policies enforced
- [ ] Rate limiting active
- [ ] CORS configured properly

### Performance
- [ ] Frontend build completes successfully
- [ ] No bundle size warnings
- [ ] Images optimized
- [ ] Fonts preloaded

### User Experience
- [ ] Login page works smoothly
- [ ] Test credentials visible on login page
- [ ] Error messages clear and helpful
- [ ] Loading states implemented
- [ ] Mobile responsive

### Documentation
- [ ] README accurate
- [ ] Setup guide complete
- [ ] Environment variable examples updated
- [ ] Deployment guide tested

---

## 🎉 You're Ready!

Once all checkboxes are complete:
1. Deploy to production
2. Test with test user
3. Invite real users
4. Monitor for issues
5. Iterate and improve

Good luck! 🚀
