from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from utils.auth import get_current_user_id, verify_user
from utils.progress_tracker import ProgressTracker, XPTracker

from agents.coach_agent import get_study_progress

router = APIRouter(
    prefix="/progress",
    tags=["progress"]
)


# Request/Response Models
class QuizAnswer(BaseModel):
    """Single quiz answer"""
    question_number: int = Field(..., ge=1, description="Question number (1-based)")
    answer: str = Field(..., min_length=1, max_length=1, description="Answer letter (A, B, C, or D)")


class EvaluateQuizRequest(BaseModel):
    """Request body for quiz evaluation"""
    study_package: Dict = Field(..., description="Complete study package from study workflow")
    answers: List[str] = Field(..., min_items=1, max_items=20, description="List of answer letters")
    difficulty: Optional[str] = Field(default='medium', description="Quiz difficulty: easy, medium, hard, expert")


class ProgressReport(BaseModel):
    """Progress report response"""
    topic: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    feedback: str
    results: List[Dict]


class UpdateXPRequest(BaseModel):
    """Request body for manual XP update"""
    points: int = Field(..., ge=1, le=1000, description="XP points to award (1-1000)")
    reason: str = Field(..., min_length=1, max_length=100, description="Reason for XP award")
    metadata: Optional[Dict] = Field(default={}, description="Additional metadata")


class ResetProgressRequest(BaseModel):
    """Request body for resetting topic progress"""
    topic: str = Field(..., min_length=1, max_length=200, description="Topic to reset")


class CalculateXPRequest(BaseModel):
    """Request body for XP calculation preview"""
    score: int = Field(..., ge=0, le=100, description="Quiz score (0-100)")
    difficulty: str = Field(default='medium', description="Difficulty: easy, medium, hard, expert")


@router.get("/")
async def get_progress_info():
    """
    Get information about progress tracking endpoints
    """
    return {
        "message": "Progress tracking and quiz evaluation",
        "endpoints": {
            "/progress/{user_id}": "GET - Fetch complete user progress and XP data",
            "/progress/calculate-xp": "POST - Calculate XP for a given score and difficulty",
            "/progress/evaluate": "POST - Evaluate quiz answers and get progress report",
            "/progress/update": "POST - Manually update XP after quiz completion",
            "/progress/reset": "POST - Reset progress for a specific topic",
            "/progress/stats": "GET - Get user's overall progress statistics",
            "/progress/topics": "GET - Get progress for all topics",
            "/progress/topics/{topic}": "GET - Get progress for specific topic",
            "/progress/xp": "GET - Get user's total XP and activity stats",
            "/progress/xp/logs": "GET - Get user's XP earning history"
        },
        "difficulty_levels": {
            "easy": "10 XP bonus",
            "medium": "20 XP bonus (default)",
            "hard": "30 XP bonus",
            "expert": "50 XP bonus"
        },
        "score_tiers": {
            "perfect": "100% - 50 XP bonus",
            "excellent": "90-99% - 30 XP bonus",
            "good": "80-89% - 15 XP bonus",
            "passing": "70-79% - 0 XP bonus"
        }
    }


@router.post("/calculate-xp")
async def calculate_xp_preview(request: CalculateXPRequest):
    """
    Calculate XP for a given score and difficulty level (preview/estimation).
    
    This endpoint allows frontends to show users how much XP they'll earn
    before submitting quiz answers. No authentication required as it's just
    a calculation utility.
    
    XP Calculation Logic:
    - Base XP: 100 points (for quiz completion)
    - Difficulty Bonus: easy=10, medium=20, hard=30, expert=50
    - Score Tier Bonus:
      * Perfect (100%): +50 XP
      * Excellent (90-99%): +30 XP
      * Good (80-89%): +15 XP
      * Passing (70-79%): +0 XP
    
    Request body:
    ```json
    {
        "score": 85,
        "difficulty": "hard"
    }
    ```
    
    Returns breakdown of XP calculation.
    """
    try:
        # Validate difficulty
        valid_difficulties = ['easy', 'medium', 'hard', 'expert']
        difficulty = request.difficulty.lower()
        if difficulty not in valid_difficulties:
            difficulty = 'medium'
        
        # Calculate XP using the core function
        total_xp = XPTracker.calculate_xp(request.score, difficulty)
        
        # Get breakdown details
        base_xp = XPTracker.XP_VALUES['quiz_completed']
        difficulty_bonus = XPTracker.get_difficulty_bonus(difficulty)
        score_tier = XPTracker.get_score_tier(float(request.score))
        performance_bonus = XPTracker.SCORE_TIER_BONUSES[score_tier]
        
        return {
            "score": request.score,
            "difficulty": difficulty,
            "total_xp": total_xp,
            "breakdown": {
                "base_xp": base_xp,
                "difficulty_bonus": difficulty_bonus,
                "performance_bonus": performance_bonus,
                "score_tier": score_tier
            },
            "message": f"Score of {request.score}% on {difficulty} difficulty = {total_xp} XP"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate XP: {str(e)}"
        )


@router.get("/{user_id}")
async def get_user_progress_and_xp(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Fetch complete user progress and XP data.
    
    Returns comprehensive user data including:
    - Progress statistics (total topics, completion rate, avg score)
    - All topic progress records
    - Total XP and activity count
    - Recent XP logs (last 10)
    
    Note: Users can only access their own data. Requesting another user's
    data will return a 403 Forbidden error.
    
    Path Parameters:
    - user_id: UUID of the user
    """
    try:
        # Security: Users can only access their own progress
        if user_id != current_user_id:
            raise HTTPException(
                status_code=403,
                detail="Forbidden: You can only access your own progress data"
            )
        
        # Fetch all user data in parallel for efficiency
        stats = await ProgressTracker.get_progress_stats(user_id)
        topics = await ProgressTracker.get_user_progress(user_id)
        xp_data = await XPTracker.get_total_xp(user_id)
        recent_xp_logs = await XPTracker.get_user_xp_logs(user_id, limit=10)
        
        return {
            "user_id": user_id,
            "statistics": stats,
            "topics": topics,
            "xp": {
                "total_xp": xp_data['total_xp'],
                "total_activities": xp_data['total_activities'],
                "last_activity": xp_data['last_activity']
            },
            "recent_xp_logs": recent_xp_logs
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch user progress: {str(e)}"
        )


@router.post("/update")
async def update_xp(
    request: UpdateXPRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Manually update XP after quiz completion or other activities.
    
    This endpoint allows awarding XP for activities like:
    - Custom quiz completions
    - Study session completions
    - Daily streak bonuses
    - Achievement unlocks
    
    Request body:
    ```json
    {
        "points": 100,
        "reason": "quiz_completed",
        "metadata": {
            "topic": "Neural Networks",
            "score": 85.0,
            "custom_field": "value"
        }
    }
    ```
    
    Returns the created XP log and updated total XP.
    """
    try:
        # Award XP
        xp_log = await XPTracker.award_xp(
            user_id=user_id,
            reason=request.reason,
            points=request.points,
            metadata=request.metadata
        )
        
        # Get updated total XP
        total_xp = await XPTracker.get_total_xp(user_id)
        
        return {
            "success": True,
            "xp_log": xp_log,
            "total_xp": total_xp['total_xp'],
            "message": f"Successfully awarded {request.points} XP for {request.reason}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update XP: {str(e)}"
        )


@router.post("/reset")
async def reset_topic_progress(
    request: ResetProgressRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Reset progress for a specific topic.
    
    This allows users to:
    - Start over on a topic they want to re-learn
    - Clear their progress to retake quizzes
    - Reset statistics for a fresh start
    
    The progress record will be deleted from the database.
    XP logs are preserved (XP earned is not removed).
    
    Request body:
    ```json
    {
        "topic": "Neural Networks"
    }
    ```
    
    Returns confirmation of reset.
    """
    try:
        # Check if progress exists
        progress = await ProgressTracker.get_user_progress(user_id, request.topic)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"No progress found for topic: {request.topic}"
            )
        
        # Delete progress record from Supabase
        from backend.config.supabase_client import supabase
        
        result = supabase.table('progress').delete().eq('user_id', user_id).eq('topic', request.topic).execute()
        
        return {
            "success": True,
            "topic": request.topic,
            "message": f"Successfully reset progress for topic: {request.topic}",
            "note": "XP earned from this topic has been preserved"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset progress: {str(e)}"
        )


@router.get("/stats")
async def get_progress_statistics(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get aggregated progress statistics for the authenticated user.
    
    Returns:
    - Total topics studied
    - Completed topics count
    - In-progress topics count
    - Average score across all topics
    - Overall completion rate
    """
    try:
        stats = await ProgressTracker.get_progress_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get progress stats: {str(e)}"
        )


@router.get("/topics")
async def get_all_topics_progress(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get progress records for all topics studied by the user.
    
    Returns list of progress records sorted by most recent attempt.
    """
    try:
        progress = await ProgressTracker.get_user_progress(user_id)
        return {
            "user_id": user_id,
            "total_topics": len(progress),
            "topics": progress
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get topics progress: {str(e)}"
        )


@router.get("/topics/{topic}")
async def get_topic_progress(
    topic: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get progress for a specific topic.
    
    Returns detailed progress record including:
    - Completion status
    - Average score
    - Total attempts
    - Last attempt timestamp
    """
    try:
        progress = await ProgressTracker.get_user_progress(user_id, topic)
        
        if not progress:
            raise HTTPException(
                status_code=404,
                detail=f"No progress found for topic: {topic}"
            )
        
        return progress[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get topic progress: {str(e)}"
        )


@router.get("/xp")
async def get_total_xp(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get total XP and activity statistics for the authenticated user.
    
    Returns:
    - Total XP earned
    - Total activities completed
    - Last activity timestamp
    """
    try:
        xp_data = await XPTracker.get_total_xp(user_id)
        return xp_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get XP data: {str(e)}"
        )


@router.get("/xp/logs")
async def get_xp_logs(
    limit: int = 50,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get XP earning history for the authenticated user.
    
    Query Parameters:
    - limit: Maximum number of logs to return (default: 50, max: 100)
    
    Returns list of XP logs with:
    - Points earned
    - Reason for earning
    - Metadata (quiz score, topic, etc.)
    - Timestamp
    """
    try:
        # Enforce max limit
        if limit > 100:
            limit = 100
        
        logs = await XPTracker.get_user_xp_logs(user_id, limit)
        
        return {
            "user_id": user_id,
            "count": len(logs),
            "logs": logs
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get XP logs: {str(e)}"
        )


@router.post("/evaluate", response_model=ProgressReport)
async def evaluate_quiz(
    request: EvaluateQuizRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Evaluate quiz answers and generate progress report.
    
    This endpoint takes a study package (from /study/complete or cached)
    and the student's quiz answers, then returns:
    - Overall score (percentage and count)
    - Personalized feedback
    - Detailed per-question analysis
    - Explanations for incorrect answers
    - Updates progress tracking in database
    - Awards XP points based on performance
    
    Example:
    ```json
    {
        "study_package": { 
            "topic": "...",
            "notes": {...},
            "quiz": [...]
        },
        "answers": ["A", "B", "C", "D", "A"]
    }
    ```
    """
    try:
        # Validate answers length matches quiz
        quiz_length = len(request.study_package.get('quiz', []))
        
        if len(request.answers) != quiz_length:
            raise HTTPException(
                status_code=400,
                detail=f"Expected {quiz_length} answers, got {len(request.answers)}"
            )
        
        # Validate answer format (A, B, C, or D)
        for i, answer in enumerate(request.answers, 1):
            if answer.upper() not in ['A', 'B', 'C', 'D']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid answer at position {i}: '{answer}'. Must be A, B, C, or D."
                )
        
        # Get progress report
        progress = await get_study_progress(
            study_package=request.study_package,
            quiz_answers=request.answers
        )
        
        # Update progress and award XP in database
        topic = request.study_package.get('topic', 'Unknown')
        score = progress['score_percentage']
        total_questions = progress['total_questions']
        correct_answers = progress['correct_answers']
        difficulty = request.difficulty or 'medium'
        
        # Validate difficulty
        valid_difficulties = ['easy', 'medium', 'hard', 'expert']
        if difficulty.lower() not in valid_difficulties:
            difficulty = 'medium'
        
        # Process quiz completion (updates progress + awards XP with difficulty bonus)
        gamification_result = await XPTracker.process_quiz_completion(
            user_id=user_id,
            topic=topic,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            difficulty=difficulty
        )
        
        # Add gamification data to response
        progress['xp_awarded'] = gamification_result['xp_awarded']['points']
        progress['total_xp'] = gamification_result['total_xp']
        progress['completion_status'] = gamification_result['completion_status']
        progress['difficulty'] = gamification_result['difficulty']
        progress['score_tier'] = gamification_result['score_tier']
        
        return progress
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate quiz: {str(e)}"
        )

