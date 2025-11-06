-- ============================================
-- CREATE TEST USER FOR STUDYQUEST
-- ============================================
-- This script creates a test user for development and testing
-- 
-- TEST USER CREDENTIALS:
-- Email: test@studyquest.dev
-- Password: testuser123
-- ============================================

-- Step 1: Create user in Supabase Auth Dashboard
-- Go to: Authentication > Users > Invite User
-- Email: test@studyquest.dev
-- Password: testuser123
-- 
-- After user is created, get the user ID from the dashboard
-- Then run the following SQL with the actual user ID:

-- Step 2: Insert user into users table
-- Replace <USER_ID_FROM_AUTH> with the actual UUID from Supabase Auth

INSERT INTO public.users (user_id, username, total_xp, level, created_at, updated_at)
VALUES (
  '<USER_ID_FROM_AUTH>', -- Replace with actual user ID from auth.users
  'testuser',
  0,
  1,
  NOW(),
  NOW()
)
ON CONFLICT (user_id) DO UPDATE
SET 
  username = EXCLUDED.username,
  updated_at = NOW();

-- Step 3: Verify user was created
SELECT user_id, username, total_xp, level, created_at
FROM public.users
WHERE username = 'testuser';

-- ============================================
-- ALTERNATIVE: Use this query if you created the user via Supabase Dashboard
-- and want to automatically get their ID
-- ============================================

-- This will create/update the user record using email lookup
WITH auth_user AS (
  SELECT id 
  FROM auth.users 
  WHERE email = 'test@studyquest.dev'
  LIMIT 1
)
INSERT INTO public.users (user_id, username, total_xp, level, created_at, updated_at)
SELECT 
  id,
  'testuser',
  0,
  1,
  NOW(),
  NOW()
FROM auth_user
ON CONFLICT (user_id) DO UPDATE
SET 
  username = EXCLUDED.username,
  updated_at = NOW();

-- ============================================
-- CLEANUP: Remove demo_user and other test data
-- ============================================

-- Delete demo_user data (run this AFTER creating test user)
DELETE FROM public.xp_logs WHERE user_id = 'demo_user';
DELETE FROM public.quiz_results WHERE user_id = 'demo_user';
DELETE FROM public.quiz_scores WHERE user_id = 'demo_user';
DELETE FROM public.user_topics WHERE user_id = 'demo_user';
DELETE FROM public.xp_history WHERE user_id = 'demo_user';
DELETE FROM public.user_badges WHERE user_id = 'demo_user';
DELETE FROM public.user_milestones WHERE user_id = 'demo_user';
DELETE FROM public.progress WHERE user_id = 'demo_user';
DELETE FROM public.users WHERE user_id = 'demo_user';

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Check test user exists
SELECT * FROM public.users WHERE username = 'testuser';

-- Check no demo_user data remains
SELECT COUNT(*) as demo_user_count FROM public.users WHERE user_id = 'demo_user';

-- Check total users
SELECT COUNT(*) as total_users FROM public.users;

-- ============================================
-- NOTES FOR DEPLOYMENT
-- ============================================
-- 
-- 1. Test user credentials are displayed on the login page
-- 2. In production, you can:
--    - Keep this test user for demos
--    - Remove it and require real signups only
--    - Change the password to something more secure
--
-- 3. Remember to run the production RLS migration:
--    migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql
--
-- 4. Ensure SUPABASE_KEY in backend .env is the ANON key, not service role
-- ============================================
