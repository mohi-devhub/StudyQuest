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


class ProgressReport(BaseModel):
    """Progress report response"""
    topic: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    feedback: str
    results: List[Dict]


@router.get("/")
async def get_progress_info():
    """
    Get information about progress tracking endpoints
    """
    return {
        "message": "Progress tracking and quiz evaluation",
        "endpoints": {
            "/progress/evaluate": "POST - Evaluate quiz answers and get progress report",
            "/progress/stats": "GET - Get user's overall progress statistics",
            "/progress/topics": "GET - Get progress for all topics",
            "/progress/topics/{topic}": "GET - Get progress for specific topic",
            "/progress/xp": "GET - Get user's total XP and activity stats",
            "/progress/xp/logs": "GET - Get user's XP earning history"
        }
    }


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
        
        # Process quiz completion (updates progress + awards XP)
        gamification_result = await XPTracker.process_quiz_completion(
            user_id=user_id,
            topic=topic,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers
        )
        
        # Add gamification data to response
        progress['xp_awarded'] = gamification_result['xp_awarded']['points']
        progress['total_xp'] = gamification_result['total_xp']
        progress['completion_status'] = gamification_result['completion_status']
        
        return progress
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate quiz: {str(e)}"
        )

