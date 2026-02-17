"""
In-memory quiz session store for server-side grading.

Prevents score forgery by keeping questions server-side and grading
answers on the backend. Sessions expire after 1 hour and cannot be
replayed once completed.
"""
import uuid
import threading
import time
from typing import Dict, List, Optional


# TTL for quiz sessions (1 hour)
SESSION_TTL_SECONDS = 3600

# Lock for thread-safe access
_lock = threading.Lock()

# session_id -> session data
_sessions: Dict[str, dict] = {}


def _cleanup_expired() -> None:
    """Remove expired sessions. Must be called with _lock held."""
    now = time.time()
    expired = [sid for sid, s in _sessions.items() if now - s["created_at"] > SESSION_TTL_SECONDS]
    for sid in expired:
        del _sessions[sid]


def create_session(
    user_id: str,
    topic: str,
    difficulty: str,
    questions: List[dict],
) -> str:
    """
    Store a quiz's questions server-side and return a session ID.

    Args:
        user_id: Owner of this session.
        topic: Quiz topic.
        difficulty: Difficulty level (easy/medium/hard/expert).
        questions: List of question dicts (must have 'answer' key).

    Returns:
        A unique session_id string.
    """
    session_id = uuid.uuid4().hex
    with _lock:
        _cleanup_expired()
        _sessions[session_id] = {
            "user_id": user_id,
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
            "completed": False,
            "created_at": time.time(),
        }
    return session_id


def grade_session(
    session_id: str,
    user_id: str,
    answers: List[str],
) -> dict:
    """
    Grade a quiz session and mark it as completed.

    Args:
        session_id: The session to grade.
        user_id: Must match the session owner.
        answers: User's selected answer letters (e.g. ["A", "B", "C"]).

    Returns:
        Dict with keys: correct, total, score, topic, difficulty, questions.

    Raises:
        ValueError: Session not found, expired, or already completed.
        PermissionError: user_id doesn't match the session owner.
    """
    with _lock:
        _cleanup_expired()

        session = _sessions.get(session_id)
        if session is None:
            raise ValueError("Quiz session not found or expired")

        if session["user_id"] != user_id:
            raise PermissionError("Not authorized to grade this session")

        if session["completed"]:
            raise ValueError("Quiz session already submitted")

        # Mark completed before releasing lock
        session["completed"] = True

        questions = session["questions"]
        topic = session["topic"]
        difficulty = session["difficulty"]

    # Grade outside of lock (read-only from here)
    total = len(questions)
    correct = 0
    graded_questions = []

    for i, q in enumerate(questions):
        user_answer = answers[i] if i < len(answers) else None
        correct_answer = q.get("answer", "")
        is_correct = user_answer == correct_answer
        if is_correct:
            correct += 1
        graded_questions.append({
            **q,
            "user_answer": user_answer,
            "is_correct": is_correct,
        })

    score = (correct / total) * 100 if total > 0 else 0

    return {
        "correct": correct,
        "total": total,
        "score": round(score, 2),
        "topic": topic,
        "difficulty": difficulty,
        "questions": graded_questions,
    }
