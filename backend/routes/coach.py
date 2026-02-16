"""
Adaptive Coach Routes
Provides personalized feedback and recommendations based on user performance
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.adaptive_coach_agent import generate_adaptive_feedback
from utils.auth import verify_user, validate_user_access

# Import rate limiter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/coach",
    tags=["adaptive-coach"]
)


class CoachFeedbackResponse(BaseModel):
    success: bool
    user_id: str
    performance_summary: Dict
    weak_topics: List[Dict]
    recommended_topics: List[str]
    motivational_messages: List[str]
    next_steps: List[str]


@router.get("/feedback/{user_id}", response_model=CoachFeedbackResponse)
@limiter.limit("5/minute")
async def get_adaptive_feedback(request: Request, user_id: str, current_user: dict = Depends(verify_user)):
    """
    Get personalized adaptive feedback for a user.
    Requires authentication. Users can only access their own feedback.
    """
    validate_user_access(user_id, current_user)
    try:
        feedback = await generate_adaptive_feedback(user_id)
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate feedback: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for coach agent"""
    return {
        "status": "healthy",
        "service": "adaptive-coach",
        "features": [
            "performance_analysis",
            "topic_recommendations", 
            "motivational_feedback"
        ]
    }
