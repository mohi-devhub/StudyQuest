-- RPC function to save quiz result atomically in a single transaction
-- This wraps the 4 sequential operations (insert quiz, update XP, update topic, log XP)
-- into a single database transaction to prevent partial writes.

CREATE OR REPLACE FUNCTION save_quiz_result_atomic(
    p_user_id TEXT,
    p_topic TEXT,
    p_difficulty TEXT,
    p_score FLOAT,
    p_total_questions INT,
    p_correct_answers FLOAT,
    p_xp_gained INT,
    p_performance_feedback TEXT,
    p_next_difficulty TEXT,
    p_quiz_data JSONB DEFAULT '{}'::JSONB,
    p_timestamp TEXT DEFAULT NULL
) RETURNS JSONB AS $$
DECLARE
    v_quiz_id UUID;
    v_current_xp INT;
    v_current_level INT;
    v_new_xp INT;
    v_new_level INT;
    v_level_up BOOLEAN;
    v_timestamp TIMESTAMPTZ;
    v_existing_progress RECORD;
BEGIN
    v_timestamp := COALESCE(p_timestamp::TIMESTAMPTZ, NOW());

    -- 1. Insert quiz result
    INSERT INTO quiz_results (user_id, topic, difficulty, score, total_questions, correct_answers, xp_gained, performance_feedback, next_difficulty, timestamp, quiz_data)
    VALUES (p_user_id, p_topic, p_difficulty, p_score, p_total_questions, p_correct_answers, p_xp_gained, p_performance_feedback, p_next_difficulty, v_timestamp, p_quiz_data)
    RETURNING id INTO v_quiz_id;

    -- 2. Update user XP and level
    SELECT COALESCE(total_xp, 0), COALESCE(current_level, 1)
    INTO v_current_xp, v_current_level
    FROM users WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        v_current_xp := 0;
        v_current_level := 1;
        INSERT INTO users (user_id, total_xp, current_level, updated_at)
        VALUES (p_user_id, p_xp_gained, FLOOR(p_xp_gained / 500) + 1, v_timestamp);
    ELSE
        v_new_xp := v_current_xp + p_xp_gained;
        v_new_level := FLOOR(v_new_xp / 500) + 1;
        UPDATE users SET total_xp = v_new_xp, current_level = v_new_level, updated_at = v_timestamp
        WHERE user_id = p_user_id;
    END IF;

    v_new_xp := COALESCE(v_new_xp, p_xp_gained);
    v_new_level := COALESCE(v_new_level, FLOOR(p_xp_gained / 500) + 1);
    v_level_up := v_new_level > v_current_level;

    -- 3. Update topic progress (upsert)
    SELECT * INTO v_existing_progress FROM progress
    WHERE user_id = p_user_id AND topic = p_topic;

    IF NOT FOUND THEN
        INSERT INTO progress (user_id, topic, avg_score, total_attempts, last_attempt, current_difficulty, best_score)
        VALUES (p_user_id, p_topic, p_score, 1, v_timestamp, p_difficulty, p_score);
    ELSE
        UPDATE progress SET
            avg_score = ROUND(((v_existing_progress.avg_score * v_existing_progress.total_attempts) + p_score) / (v_existing_progress.total_attempts + 1), 2),
            total_attempts = v_existing_progress.total_attempts + 1,
            last_attempt = v_timestamp,
            current_difficulty = p_difficulty,
            best_score = GREATEST(v_existing_progress.best_score, p_score)
        WHERE user_id = p_user_id AND topic = p_topic;
    END IF;

    -- 4. Log XP gain
    INSERT INTO xp_logs (user_id, xp_amount, source, topic, timestamp, details)
    VALUES (p_user_id, p_xp_gained, 'quiz_completion', p_topic, v_timestamp, jsonb_build_object('quiz_id', v_quiz_id, 'score', p_score, 'difficulty', p_difficulty));

    -- Return result
    RETURN jsonb_build_object(
        'quiz_id', v_quiz_id,
        'user_id', p_user_id,
        'xp_gained', p_xp_gained,
        'total_xp', v_new_xp,
        'current_level', v_new_level,
        'level_up', v_level_up,
        'timestamp', v_timestamp
    );
END;
$$ LANGUAGE plpgsql;
