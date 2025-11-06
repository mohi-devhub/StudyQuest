-- ============================================
-- CLEAN UP ALL DEMO AND MOCK DATA
-- ============================================
-- Run this script to remove all test/demo data from production database
-- CAUTION: This will delete all data except the test user
-- ============================================

BEGIN;

-- ============================================
-- 1. CLEAN UP DEMO_USER DATA
-- ============================================

-- Delete all demo_user related data
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
-- 2. CLEAN UP OTHER TEST DATA
-- ============================================

-- Delete any other test users (keeping only real authenticated users)
-- This preserves users from auth.users table
DELETE FROM public.users 
WHERE user_id NOT IN (
  SELECT id FROM auth.users
);

-- Clean up orphaned progress records
DELETE FROM public.progress 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned XP logs
DELETE FROM public.xp_logs 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned quiz results
DELETE FROM public.quiz_results 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned quiz scores
DELETE FROM public.quiz_scores 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned user topics
DELETE FROM public.user_topics 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned XP history
DELETE FROM public.xp_history 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned badges
DELETE FROM public.user_badges 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- Clean up orphaned milestones
DELETE FROM public.user_milestones 
WHERE user_id NOT IN (
  SELECT user_id FROM public.users
);

-- ============================================
-- 3. VERIFICATION QUERIES
-- ============================================

-- Show remaining users
SELECT user_id, username, total_xp, level, created_at
FROM public.users
ORDER BY created_at DESC;

-- Show data counts per table
SELECT 
  'users' as table_name, COUNT(*) as record_count FROM public.users
UNION ALL
SELECT 'progress', COUNT(*) FROM public.progress
UNION ALL
SELECT 'xp_logs', COUNT(*) FROM public.xp_logs
UNION ALL
SELECT 'quiz_results', COUNT(*) FROM public.quiz_results
UNION ALL
SELECT 'quiz_scores', COUNT(*) FROM public.quiz_scores
UNION ALL
SELECT 'user_topics', COUNT(*) FROM public.user_topics
UNION ALL
SELECT 'xp_history', COUNT(*) FROM public.xp_history
UNION ALL
SELECT 'user_badges', COUNT(*) FROM public.user_badges
UNION ALL
SELECT 'user_milestones', COUNT(*) FROM public.user_milestones;

-- Check for any demo_user remnants
SELECT 'demo_user found!' as warning, COUNT(*) as count
FROM public.users
WHERE user_id = 'demo_user'
HAVING COUNT(*) > 0;

COMMIT;

-- ============================================
-- POST-CLEANUP STEPS
-- ============================================
-- After running this script:
--
-- 1. Verify the test user still exists:
--    SELECT * FROM users WHERE username = 'testuser';
--
-- 2. Verify no orphaned data:
--    Run the verification queries above
--
-- 3. Test the application:
--    - Login with test user
--    - Create a quiz
--    - Check progress tracking
--    - Verify XP system works
--
-- 4. Optional: Reset test user to clean state:
--    UPDATE users SET total_xp = 0, level = 1 
--    WHERE username = 'testuser';
-- ============================================
