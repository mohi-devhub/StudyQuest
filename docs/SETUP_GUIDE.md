# StudyQuest Setup Guide

Complete guide to set up StudyQuest locally or deploy to production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Authentication Setup](#authentication-setup)
7. [Production Deployment](#production-deployment)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software
- **Node.js** 18.x or higher
- **Python** 3.11 or higher
- **npm** or **yarn**
- **Git**

### Required Accounts
- **Supabase Account** - [supabase.com](https://supabase.com)
- **OpenRouter API Key** - [openrouter.ai](https://openrouter.ai)

---

## Environment Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd StudyQuest
```

### 2. Backend Environment Variables

Create `backend/.env`:
```bash
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key  # Use ANON key, NOT service role
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key  # Only for admin operations

# API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key

# Security Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
ENVIRONMENT=development  # or 'production'

# JWT Configuration (from Supabase project settings)
JWT_SECRET=your_supabase_jwt_secret
```

**How to get Supabase keys:**
1. Go to your Supabase project dashboard
2. Settings → API
3. Copy `Project URL` as `SUPABASE_URL`
4. Copy `anon public` key as `SUPABASE_KEY`
5. Copy `service_role` key as `SUPABASE_SERVICE_ROLE_KEY`
6. Copy `JWT Secret` from Project Settings → API → JWT Settings

### 3. Frontend Environment Variables

Create `frontend/.env.local`:
```bash
# Supabase Configuration (same as backend)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Database Setup

### 1. Create Supabase Project
1. Go to [supabase.com](https://supabase.com)
2. Create new project
3. Note down the database password

### 2. Run Database Migrations

Navigate to Supabase SQL Editor and run these scripts in order:

#### A. Create Schema
```sql
-- Run: SUPABASE_SCHEMA.sql
```
This creates all necessary tables (users, progress, xp_logs, quiz_results, badges, etc.)

#### B. Set Up RLS Policies
For development (allows test user):
```sql
-- Run: migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql
```

For production (requires authentication):
```sql
-- Run: migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql
```

#### C. Create Test User
```sql
-- Run: migrations/CREATE_TEST_USER.sql
```

**Manual Steps for Test User:**
1. Go to Supabase Dashboard → Authentication → Users
2. Click "Invite User" or "Add User"
3. Email: `test@studyquest.dev`
4. Password: `testuser123`
5. Copy the generated user ID
6. Run the SQL script and replace `<USER_ID_FROM_AUTH>` with the actual ID

Or use the automatic query in the script that looks up by email.

### 3. Verify Database Setup

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check RLS policies
SELECT tablename, policyname 
FROM pg_policies 
WHERE schemaname = 'public';

-- Check test user exists
SELECT * FROM users WHERE username = 'testuser';
```

---

## Backend Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Verify Installation
```bash
# Check Python version
python --version  # Should be 3.11+

# Check installed packages
pip list | grep -E "fastapi|supabase|langchain"
```

### 3. Run Backend Server
```bash
# Development mode with auto-reload
uvicorn main:app --reload --port 8000

# Or use the run script
python main.py
```

### 4. Test Backend
```bash
# Check health endpoint
curl http://localhost:8000/

# Should return: {"status": "healthy", "message": "StudyQuest API is running"}
```

---

## Frontend Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Verify Installation
```bash
# Check Node version
node --version  # Should be 18+

# Check Next.js installation
npm list next
```

### 3. Run Frontend
```bash
# Development mode
npm run dev

# Production build
npm run build
npm run start
```

### 4. Access Application
Open browser to: [http://localhost:3000](http://localhost:3000)

You should see the login page.

---

## Authentication Setup

### 1. Configure Supabase Auth

In Supabase Dashboard → Authentication → Settings:

#### Email Auth
- Enable Email provider
- Disable email confirmations for testing (enable in production)
- Set site URL: `http://localhost:3000` (development)

#### URL Configuration
- Site URL: `http://localhost:3000`
- Redirect URLs: `http://localhost:3000/**`

### 2. Test Authentication Flow

1. **Sign Up**
   - Go to http://localhost:3000/signup
   - Create account with any email
   - Or use test credentials

2. **Login**
   - Go to http://localhost:3000/login
   - Use test credentials:
     - Email: `test@studyquest.dev`
     - Password: `testuser123`

3. **Protected Routes**
   - After login, you'll be redirected to `/dashboard`
   - Try accessing `/progress`, `/achievements`, etc.
   - Logout and verify redirect to `/login`

### 3. Verify Auth Integration

Check browser console and network tab:
- Should see Supabase auth cookies
- API calls should include auth headers
- No 401 errors on protected routes

---

## Production Deployment

### 1. Backend Deployment (Railway/Render/AWS)

#### Railway Example:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
cd backend
railway up
```

#### Environment Variables (Production):
```bash
SUPABASE_URL=your_production_supabase_url
SUPABASE_KEY=your_production_anon_key
OPENROUTER_API_KEY=your_api_key
ALLOWED_ORIGINS=https://your-domain.vercel.app
ENVIRONMENT=production
```

### 2. Frontend Deployment (Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

#### Environment Variables (Vercel):
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_URL` (your backend URL)

### 3. Database Migration (Production)

Before deploying, run production RLS migration:

```sql
-- In Supabase SQL Editor
-- Run: migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql
```

This removes demo_user exceptions and enforces authentication.

### 4. Clean Up Demo Data

```sql
-- Run: migrations/CLEANUP_DEMO_DATA.sql
```

This removes all demo/test data except the test user.

### 5. Post-Deployment Checklist

- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] Login works with test user
- [ ] Sign up creates new user
- [ ] Protected routes redirect to login when not authenticated
- [ ] Quiz generation works
- [ ] Progress tracking updates
- [ ] XP system functions
- [ ] No console errors
- [ ] CORS configured correctly
- [ ] Rate limiting active

---

## Troubleshooting

### Common Issues

#### 1. "Supabase connection failed"
**Cause:** Wrong credentials or network issue

**Solution:**
```bash
# Verify .env file
cat backend/.env | grep SUPABASE

# Test connection
python -c "from supabase import create_client; print(create_client('URL', 'KEY'))"
```

#### 2. "401 Unauthorized" on API calls
**Cause:** Using service role key instead of anon key

**Solution:**
- Check `SUPABASE_KEY` in backend/.env
- Should be anon key, not service_role key
- Service role bypasses RLS

#### 3. "RLS policy violation"
**Cause:** RLS policies not set up or wrong key

**Solution:**
```sql
-- Check policies exist
SELECT * FROM pg_policies WHERE schemaname = 'public';

-- Ensure using anon key in backend
-- Ensure production migration ran if in production
```

#### 4. Login redirects to login page (infinite loop)
**Cause:** Middleware or auth state issue

**Solution:**
```bash
# Clear browser cookies
# Check middleware.ts is correct
# Verify useAuth hook works
# Check browser console for errors
```

#### 5. "Cannot find module" errors
**Cause:** Dependencies not installed

**Solution:**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

#### 6. CORS errors in browser
**Cause:** ALLOWED_ORIGINS not configured

**Solution:**
```bash
# backend/.env
ALLOWED_ORIGINS=http://localhost:3000

# Or for production
ALLOWED_ORIGINS=https://your-domain.vercel.app
```

#### 7. Rate limit errors (429)
**Cause:** Too many requests (expected behavior)

**Solution:**
- Wait 1 minute
- Or adjust rate limit in backend/main.py
- Default: 10 requests/minute

---

## Development Tips

### Hot Reload
- Backend: uvicorn auto-reloads on file changes
- Frontend: Next.js auto-reloads on save

### Database Inspection
```bash
# Use Supabase Table Editor
# Or connect via psql:
psql postgresql://postgres:[PASSWORD]@[PROJECT-REF].supabase.co:5432/postgres
```

### API Testing
```bash
# Use curl
curl -X POST http://localhost:8000/study/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"Python","difficulty":"easy"}'

# Or use Postman/Insomnia
```

### Logs
```bash
# Backend logs
# Terminal where uvicorn is running

# Frontend logs
# Browser console (F12)
# Terminal where npm run dev is running
```

---

## Next Steps

1. **Customize Test User**
   - Change password
   - Add more test data
   - Create multiple test users

2. **Configure AI Models**
   - Adjust OpenRouter models in backend/routes
   - Tune prompt templates
   - Test different model parameters

3. **Add Features**
   - Google OAuth (optional)
   - Email verification
   - Password reset
   - User profiles

4. **Monitor Performance**
   - Set up Sentry for error tracking
   - Configure logging
   - Monitor API usage

5. **Scale**
   - Add Redis for caching
   - Implement background jobs
   - Optimize database queries
   - Add CDN for static assets

---

## Support

- **Issues:** Create GitHub issue
- **Docs:** See `/docs` folder for API reference
- **Supabase Docs:** [supabase.com/docs](https://supabase.com/docs)
- **Next.js Docs:** [nextjs.org/docs](https://nextjs.org/docs)
- **FastAPI Docs:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
