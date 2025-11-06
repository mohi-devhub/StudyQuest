-- =====================================================
-- RESET LEADERBOARD - Clean Start
-- =====================================================
-- This script resets the leaderboard by:
-- 1. Deleting all user data except test user
-- 2. Resetting test user's XP and level to 0
-- 3. Cleaning up related data (quiz attempts, achievements, etc.)
--
-- WARNING: This will delete ALL user data except test@studyquest.dev
-- =====================================================

BEGIN;

-- Store test user ID for safety
DO $$
DECLARE
    test_user_id TEXT;
BEGIN
    -- Get test user ID (cast to text)
    SELECT id::text INTO test_user_id
    FROM auth.users
    WHERE email = 'test@studyquest.dev'
    LIMIT 1;

    IF test_user_id IS NULL THEN
        RAISE NOTICE 'Warning: Test user not found. Please create test@studyquest.dev first.';
        ROLLBACK;
        RETURN;
    END IF;

    RAISE NOTICE 'Test user ID: %', test_user_id;

    -- Delete all quiz attempts except test user (if table exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'quiz_attempts') THEN
        DELETE FROM quiz_attempts WHERE user_id != test_user_id;
        RAISE NOTICE 'Deleted quiz attempts';
    END IF;

    -- Delete all study sessions except test user (if table exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'study_sessions') THEN
        DELETE FROM study_sessions WHERE user_id != test_user_id;
        RAISE NOTICE 'Deleted study sessions';
    END IF;

    -- Delete all achievements except test user (if table exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_achievements') THEN
        DELETE FROM user_achievements WHERE user_id != test_user_id;
        RAISE NOTICE 'Deleted user achievements';
    END IF;

    -- Delete all notes except test user (if table exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notes') THEN
        DELETE FROM notes WHERE user_id != test_user_id;
        RAISE NOTICE 'Deleted notes';
    END IF;

    -- Delete all user progress except test user (if table exists)
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_progress') THEN
        DELETE FROM user_progress WHERE user_id != test_user_id;
        RAISE NOTICE 'Deleted user progress';
    END IF;

    -- Delete all users except test user from public.users
    DELETE FROM users
    WHERE user_id != test_user_id;
    RAISE NOTICE 'Deleted other users from public.users';

    -- Reset test user's XP and level to 0
    UPDATE users
    SET 
        total_xp = 0,
        level = 1,
        updated_at = NOW()
    WHERE user_id = test_user_id;
    RAISE NOTICE 'Reset test user XP and level';

    -- Delete test user's quiz attempts (optional - uncomment if you want a completely fresh start)
    -- IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'quiz_attempts') THEN
    --     DELETE FROM quiz_attempts WHERE user_id = test_user_id;
    -- END IF;
    -- IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'study_sessions') THEN
    --     DELETE FROM study_sessions WHERE user_id = test_user_id;
    -- END IF;
    -- IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_achievements') THEN
    --     DELETE FROM user_achievements WHERE user_id = test_user_id;
    -- END IF;
    -- IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'notes') THEN
    --     DELETE FROM notes WHERE user_id = test_user_id;
    -- END IF;
    -- IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_progress') THEN
    --     DELETE FROM user_progress WHERE user_id = test_user_id;
    -- END IF;

    RAISE NOTICE '✓ Leaderboard reset complete!';
    RAISE NOTICE 'Test user (test@studyquest.dev) has been reset to 0 XP, Level 1';
END $$;

COMMIT;

-- Verify the reset
SELECT 
    username,
    total_xp,
    level,
    created_at,
    updated_at
FROM users
ORDER BY total_xp DESC;

-- Show quiz attempts count (if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'quiz_attempts') THEN
        RAISE NOTICE 'Quiz attempts per user:';
        PERFORM u.username, COUNT(qa.id) as quiz_attempts
        FROM users u
        LEFT JOIN quiz_attempts qa ON u.user_id = qa.user_id
        GROUP BY u.username
        ORDER BY quiz_attempts DESC;
    ELSE
        RAISE NOTICE 'quiz_attempts table does not exist';
    END IF;
END $$;
