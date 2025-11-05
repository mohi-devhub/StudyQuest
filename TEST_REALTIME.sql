-- ===========================================================================
-- TEST REAL-TIME UPDATES
-- ===========================================================================
-- Run these SQL statements in Supabase SQL Editor to test real-time features
-- ===========================================================================

-- Test 1: Add XP for demo_user (should trigger toast notification)
INSERT INTO public.xp_logs (user_id, xp_amount, source, topic)
VALUES ('demo_user', 100, 'quiz_complete', 'Real-time Test');

-- Test 2: Update demo_user's total XP in users table (should update XP bar)
UPDATE public.users 
SET total_xp = total_xp + 100
WHERE user_id = 'demo_user';

-- Test 3: Update a topic progress (should update topic card)
UPDATE public.progress
SET avg_score = 95.0
WHERE user_id = 'demo_user' AND topic = 'JavaScript Basics';

-- Test 4: Level up demo_user (should show "LEVEL UP!" toast)
-- First check current level:
SELECT user_id, total_xp, level FROM public.users WHERE user_id = 'demo_user';

-- Then update to next level:
UPDATE public.users 
SET total_xp = 3000, level = 6
WHERE user_id = 'demo_user';

-- ===========================================================================
-- LEADERBOARD TEST
-- ===========================================================================

-- The leaderboard shows users from the 'users' table, NOT xp_logs
-- To see a user on leaderboard, they must exist in the users table

-- View current leaderboard:
SELECT user_id, username, total_xp, level 
FROM public.users 
ORDER BY total_xp DESC 
LIMIT 10;

-- Add a new user to leaderboard:
INSERT INTO public.users (user_id, username, total_xp, level, email)
VALUES ('test_user', 'TestUser123', 4000, 8, 'test@example.com')
ON CONFLICT (username) DO UPDATE 
SET total_xp = 4000, level = 8;

-- Update existing user's XP (should update leaderboard position):
UPDATE public.users 
SET total_xp = 6000, level = 12
WHERE username = 'CodeMaster3000';

-- ===========================================================================
-- VERIFY REAL-TIME IS WORKING
-- ===========================================================================

-- Check browser console should show:
-- "🎉 New XP gained: ..." when you insert xp_logs
-- "👤 User updated: ..." when you update users table
-- "📊 Progress updated: ..." when you update progress table

-- Dashboard should:
-- - Show toast notification for XP gains
-- - Update XP bar smoothly
-- - Update topic cards when progress changes
-- - Show "LEVEL UP!" toast when level increases

-- Leaderboard should:
-- - Update rankings instantly when users table changes
-- - Re-sort users by total_xp
-- - Highlight current user (demo_user)

-- ===========================================================================
-- CLEANUP
-- ===========================================================================

-- Reset demo_user to original state:
UPDATE public.users 
SET total_xp = 2450, level = 5
WHERE user_id = 'demo_user';

-- Remove test XP logs:
DELETE FROM public.xp_logs 
WHERE user_id = 'demo_user' 
AND source = 'quiz_complete' 
AND topic = 'Real-time Test';

-- Remove test user:
DELETE FROM public.users WHERE user_id = 'test_user';
