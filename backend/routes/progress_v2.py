"""
Enhanced Progress Tracking Routes (V2)
Uses new tables: user_topics, quiz_scores, xp_history
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from utils.auth import verify_user, validate_user_access
from utils.error_handlers import (
    validate_topic,
    validate_difficulty,
    handle_database_error,
    ErrorResponse
)

# Supabase client
from config.supabase_client import supabase

router = APIRouter(
    prefix="/progress/v2",
    tags=["progress-v2"]
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class QuizSubmission(BaseModel):
    """Request body for quiz submission"""
    user_id: str = Field(..., description="User ID")
    topic: str = Field(..., min_length=1, max_length=50, description="Topic name (max 50 chars)")
    difficulty: str = Field(default='medium', description="easy, medium, hard, expert")
    correct: int = Field(..., ge=0, description="Number of correct answers")
    total: int = Field(..., ge=1, le=50, description="Total number of questions")
    time_taken: Optional[int] = Field(None, ge=0, description="Time taken in seconds")
    answers: Optional[List[str]] = Field(default=[], description="User answers")
    questions: Optional[List[Dict]] = Field(default=[], description="Quiz questions")
    metadata: Optional[Dict] = Field(default={}, description="Additional data")


class TopicProgress(BaseModel):
    """Response model for topic progress"""
    user_id: str
    topic: str
    status: str
    score: float
    best_score: float
    attempts: int
    time_spent: int
    last_attempted_at: Optional[datetime]
    completed_at: Optional[datetime]


class XPChange(BaseModel):
    """XP change event"""
    xp_change: int
    reason: str
    topic: Optional[str]
    previous_xp: int
    new_xp: int
    previous_level: int
    new_level: int


# ============================================================================
# XP CALCULATION UTILITIES
# ============================================================================

def calculate_xp(correct: int, total: int, difficulty: str) -> int:
    """
    Calculate XP earned from a quiz.
    
    Formula:
    - Base: 100 XP
    - Difficulty bonus: easy=10, medium=20, hard=30, expert=50
    - Score tier bonus:
      * 100%: +50 XP
      * 90-99%: +30 XP
      * 80-89%: +15 XP
      * 70-79%: +0 XP
    """
    base_xp = 100
    
    # Difficulty bonuses
    difficulty_bonus = {
        'easy': 10,
        'medium': 20,
        'hard': 30,
        'expert': 50
    }.get(difficulty.lower(), 20)
    
    # Calculate score percentage
    score = (correct / total) * 100 if total > 0 else 0
    
    # Score tier bonuses
    if score == 100:
        score_bonus = 50
    elif score >= 90:
        score_bonus = 30
    elif score >= 80:
        score_bonus = 15
    elif score >= 70:
        score_bonus = 0
    else:
        score_bonus = 0
    
    total_xp = base_xp + difficulty_bonus + score_bonus
    return total_xp


def calculate_level(total_xp: int) -> int:
    """Calculate level from total XP (500 XP per level)"""
    return (total_xp // 500) + 1


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/")
async def get_progress_v2_info():
    """Information about enhanced progress tracking endpoints"""
    return {
        "message": "Enhanced Progress Tracking API v2",
        "version": "2.0",
        "endpoints": {
            "POST /submit-quiz": "Submit quiz and auto-update progress",
            "GET /user/{user_id}": "Get complete user progress",
            "GET /user/{user_id}/topics": "Get all topics for user",
            "GET /user/{user_id}/topics/{topic}": "Get specific topic progress",
            "GET /user/{user_id}/xp-history": "Get XP change history",
            "GET /user/{user_id}/quiz-history": "Get quiz attempt history",
            "GET /user/{user_id}/stats": "Get user statistics",
            "GET /leaderboard": "Get XP leaderboard with details"
        },
        "features": [
            "Automatic XP calculation",
            "Auto-update progress on quiz submission",
            "Detailed topic tracking with status",
            "Complete XP history with before/after",
            "Quiz attempt history"
        ]
    }



@router.post("/submit-quiz")
async def submit_quiz(
    submission: QuizSubmission,
    current_user: dict = Depends(verify_user)
):
    """
    Submit a quiz and automatically update:
    - quiz_scores table
    - user_topics (via trigger)
    - xp_history (via trigger)
    - users.total_xp
    
    Features:
    - Input validation (topic ≤ 50 chars, difficulty validation)
    - Standardized error responses
    - Graceful database error handling
    
    Requires authentication. Uses authenticated user_id instead of submission.user_id.
    
    Returns the quiz result and XP earned.
    """
    try:
        # Use authenticated user ID (ignore submission.user_id)
        user_id = current_user.id
        
        # Validate inputs
        validated_topic = validate_topic(submission.topic, max_length=50)
        validated_difficulty = validate_difficulty(submission.difficulty)
        
        # Validate score
        if submission.correct > submission.total:
            raise HTTPException(
                status_code=400,
                detail={
                    "status": "error",
                    "message": "Correct answers cannot exceed total questions",
                    "code": "VALIDATION_ERROR"
                }
            )
        
        # Calculate score and XP
        score = (submission.correct / submission.total) * 100
        xp_earned = calculate_xp(submission.correct, submission.total, validated_difficulty)
        
        # Get or create user
        try:
            user_result = supabase.table('users').select('total_xp, level, username').eq(
                'user_id', user_id
            ).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                # User doesn't exist, create them
                print(f"Creating new user: {user_id}")
                new_user = supabase.table('users').insert({
                    'user_id': user_id,
                    'username': f'user_{user_id[:8]}',  # Generate username from ID
                    'total_xp': 0,
                    'level': 1
                }).execute()
                
                if new_user.data:
                    previous_xp = 0
                    previous_level = 1
                else:
                    raise Exception("Failed to create user")
            else:
                user_data = user_result.data[0]
                previous_xp = user_data.get('total_xp', 0)
                previous_level = user_data.get('level', 1)
                
        except HTTPException:
            raise
        except Exception as e:
            print(f"User lookup/create error: {str(e)}")
            # If user lookup fails, use defaults and continue
            previous_xp = 0
            previous_level = 1
        
        new_xp = previous_xp + xp_earned
        new_level = calculate_level(new_xp)
        
        # Insert quiz score (triggers will auto-update user_topics)
        try:
            quiz_result = supabase.table('quiz_scores').insert({
                'user_id': user_id,
                'topic': validated_topic,
                'difficulty': validated_difficulty,
                'correct': submission.correct,
                'total': submission.total,
                'score': score,
                'xp_gained': xp_earned,
                'time_taken': submission.time_taken,
                'answers': submission.answers,
                'questions': submission.questions,
                'metadata': submission.metadata
            }).execute()
        except Exception as e:
            print(f"Quiz score insertion error: {str(e)}")
            raise handle_database_error("quiz submission")
        
        # Insert XP history
        try:
            xp_history_result = supabase.table('xp_history').insert({
                'user_id': user_id,
                'xp_change': xp_earned,
                'reason': 'quiz_complete',
                'topic': validated_topic,
                'quiz_id': quiz_result.data[0]['id'],
                'previous_xp': previous_xp,
                'new_xp': new_xp,
                'previous_level': previous_level,
                'new_level': new_level,
                'metadata': {
                    'score': score,
                    'difficulty': validated_difficulty,
                    'correct': submission.correct,
                    'total': submission.total
                }
            }).execute()
        except Exception as e:
            print(f"XP history insertion error: {str(e)}")
            # Continue even if XP history fails
        
        # Update user's total XP and level
        try:
            print(f"Updating user {user_id}: previous_xp={previous_xp}, new_xp={new_xp}, xp_earned={xp_earned}")
            
            # Try updating with match
            user_update = supabase.table('users').update({
                'total_xp': new_xp,
                'level': new_level
            }).match({'user_id': user_id}).execute()
            
            print(f"User update result: {user_update.data}")
            print(f"User update count: {user_update.count if hasattr(user_update, 'count') else 'N/A'}")
            
            if not user_update.data or len(user_update.data) == 0:
                print(f"WARNING: User update returned no data. Checking if user exists...")
                # Verify user exists
                check_user = supabase.table('users').select('user_id, total_xp').eq('user_id', user_id).execute()
                print(f"User check result: {check_user.data}")
                
                if check_user.data:
                    print(f"ERROR: User exists but update failed!")
                else:
                    print(f"ERROR: User {user_id} not found in database!")
        except Exception as e:
            print(f"User update error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise handle_database_error("user XP update")
        
        # Also insert into xp_logs for backward compatibility
        try:
            xp_log = supabase.table('xp_logs').insert({
                'user_id': user_id,
                'xp_amount': xp_earned,
                'source': 'quiz_complete',
                'topic': validated_topic,
                'metadata': {
                    'score': score,
                    'difficulty': validated_difficulty,
                    'quiz_id': quiz_result.data[0]['id']
                }
            }).execute()
        except Exception as e:
            print(f"XP log insertion error: {str(e)}")
            # Continue even if xp_logs fails (backward compatibility table)
        
        return {
            "status": "success",
            "quiz_id": quiz_result.data[0]['id'],
            "score": round(score, 2),
            "correct": submission.correct,
            "total": submission.total,
            "xp_earned": xp_earned,
            "xp_change": {
                "previous_xp": previous_xp,
                "new_xp": new_xp,
                "previous_level": previous_level,
                "new_level": new_level,
                "leveled_up": new_level > previous_level
            },
            "feedback": get_feedback(score)
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        print(f"Quiz submission error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to submit quiz. Please try again.",
                "code": "SUBMISSION_ERROR"
            }
        )


@router.get("/{user_id}")
async def get_user_progress(user_id: str, current_user: dict = Depends(verify_user)):
    """Get complete user progress including all topics and XP"""
    validate_user_access(user_id, current_user)
    try:
        # Get user data
        user = supabase.table('users').select('*').eq('user_id', user_id).execute()
        
        # Create user if doesn't exist
        if not user.data or len(user.data) == 0:
            print(f"User {user_id} not found, creating...")
            new_user = supabase.table('users').insert({
                'user_id': user_id,
                'username': f'user_{user_id[:8]}',
                'total_xp': 0,
                'level': 1
            }).execute()
            
            if new_user.data:
                user.data = new_user.data
            else:
                raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Get all topics
        topics = supabase.table('user_topics').select('*').eq('user_id', user_id).execute()
        
        # Transform topics to match frontend expectations
        transformed_topics = [
            {
                'topic': t['topic'],
                'avg_score': t.get('best_score', 0),  # Map best_score to avg_score
                'total_attempts': t.get('attempts', 0),  # Map attempts to total_attempts
                'last_attempt': t.get('last_attempted_at'),  # Map last_attempted_at to last_attempt
                'status': t.get('status'),
                'created_at': t.get('created_at'),
                'updated_at': t.get('updated_at')
            }
            for t in (topics.data or [])
        ]
        
        # Get recent XP history
        xp_history = supabase.table('xp_history').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        
        # Get quiz count
        quiz_count = supabase.table('quiz_scores').select('id', count='exact').eq('user_id', user_id).execute()
        
        return {
            "user": user.data[0] if user.data else None,  # Return single user object, not array
            "topics": transformed_topics,
            "recent_xp_history": xp_history.data,
            "total_quizzes": quiz_count.count,
            "stats": calculate_user_stats(topics.data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user progress: {str(e)}")


@router.get("/user/{user_id}/topics")
async def get_user_topics(user_id: str, status: Optional[str] = None, current_user: dict = Depends(verify_user)):
    """Get all topics for a user, optionally filtered by status"""
    validate_user_access(user_id, current_user)
    try:
        query = supabase.table('user_topics').select('*').eq('user_id', user_id)
        
        if status:
            query = query.eq('status', status)
        
        result = query.order('last_attempted_at', desc=True).execute()
        
        return {
            "user_id": user_id,
            "topics": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")


@router.get("/user/{user_id}/topics/{topic}")
async def get_topic_progress(user_id: str, topic: str, current_user: dict = Depends(verify_user)):
    """Get progress for a specific topic"""
    validate_user_access(user_id, current_user)
    try:
        # Get topic progress
        topic_data = supabase.table('user_topics').select('*').eq('user_id', user_id).eq('topic', topic).single().execute()
        
        if not topic_data.data:
            return {
                "user_id": user_id,
                "topic": topic,
                "status": "not_started",
                "message": "No attempts yet"
            }
        
        # Get quiz history for this topic
        quizzes = supabase.table('quiz_scores').select('*').eq('user_id', user_id).eq('topic', topic).order('created_at', desc=True).execute()
        
        return {
            "progress": topic_data.data,
            "quiz_history": quizzes.data,
            "total_attempts": len(quizzes.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topic progress: {str(e)}")


@router.get("/user/{user_id}/xp-history")
async def get_xp_history(user_id: str, limit: int = 50, current_user: dict = Depends(verify_user)):
    """Get XP change history for a user"""
    validate_user_access(user_id, current_user)
    try:
        result = supabase.table('xp_history').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(limit).execute()
        
        return {
            "user_id": user_id,
            "history": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get XP history: {str(e)}")


@router.get("/user/{user_id}/quiz-history")
async def get_quiz_history(user_id: str, limit: int = 50, topic: Optional[str] = None, current_user: dict = Depends(verify_user)):
    """Get quiz attempt history"""
    validate_user_access(user_id, current_user)
    try:
        query = supabase.table('quiz_scores').select('*').eq('user_id', user_id)
        
        if topic:
            query = query.eq('topic', topic)
        
        result = query.order('created_at', desc=True).limit(limit).execute()
        
        return {
            "user_id": user_id,
            "quizzes": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quiz history: {str(e)}")


@router.get("/user/{user_id}/stats")
async def get_user_stats(user_id: str, current_user: dict = Depends(verify_user)):
    """Get aggregated user statistics"""
    validate_user_access(user_id, current_user)
    try:
        # Use the view we created
        stats = supabase.table('user_progress_summary').select('*').eq('user_id', user_id).execute()
        
        # Get user data
        user = supabase.table('users').select('total_xp, level').eq('user_id', user_id).execute()
        
        # Get stats from view or defaults
        progress_stats = stats.data[0] if stats.data and len(stats.data) > 0 else {
            "total_topics": 0,
            "mastered_count": 0,
            "completed_count": 0,
            "in_progress_count": 0,
            "avg_best_score": 0,
            "total_attempts": 0,
            "total_time_spent": 0
        }
        
        # Get user info
        user_info = user.data[0] if user.data and len(user.data) > 0 else {
            "total_xp": 0,
            "level": 1
        }
        
        # Return flat structure for frontend compatibility
        return {
            "user_id": user_id,
            "total_xp": user_info.get('total_xp', 0),
            "level": user_info.get('level', 1),
            "topics_started": progress_stats.get('total_topics', 0),
            "topics_mastered": progress_stats.get('mastered_count', 0),
            "topics_completed": progress_stats.get('completed_count', 0),
            "topics_in_progress": progress_stats.get('in_progress_count', 0),
            "average_score": progress_stats.get('avg_best_score', 0),
            "quizzes_completed": progress_stats.get('total_attempts', 0),
            "total_time_spent": progress_stats.get('total_time_spent', 0)
        }
        
    except Exception as e:
        print(f"Error getting user stats: {str(e)}")
        # Return default stats on error
        return {
            "user_id": user_id,
            "total_xp": 0,
            "level": 1,
            "topics_started": 0,
            "topics_mastered": 0,
            "topics_completed": 0,
            "topics_in_progress": 0,
            "average_score": 0,
            "quizzes_completed": 0,
            "total_time_spent": 0
        }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get XP leaderboard with detailed stats"""
    try:
        # Use the detailed leaderboard view
        result = supabase.table('xp_leaderboard_detailed').select('*').limit(limit).execute()
        
        return {
            "leaderboard": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get leaderboard: {str(e)}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_feedback(score: float) -> str:
    """Generate feedback based on score"""
    if score >= 95:
        return "Perfect! Outstanding mastery! [***]"
    elif score >= 90:
        return "Excellent work! You've mastered this topic! [++]"
    elif score >= 80:
        return "Great job! Solid understanding demonstrated! [+]"
    elif score >= 70:
        return "Good effort! Keep practicing to improve! [=]"
    elif score >= 50:
        return "Fair attempt. Review the material and try again! [-]"
    else:
        return "Keep learning! Practice makes perfect! [>]"


def calculate_user_stats(topics: List[Dict]) -> Dict:
    """Calculate aggregated statistics from topics"""
    if not topics:
        return {
            "total_topics": 0,
            "mastered": 0,
            "completed": 0,
            "in_progress": 0,
            "avg_score": 0
        }
    
    return {
        "total_topics": len(topics),
        "mastered": len([t for t in topics if t['status'] == 'mastered']),
        "completed": len([t for t in topics if t['status'] == 'completed']),
        "in_progress": len([t for t in topics if t['status'] == 'in_progress']),
        "avg_score": round(sum(t['best_score'] for t in topics) / len(topics), 2)
    }
