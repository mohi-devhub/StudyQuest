"""
Adaptive Coach Routes
Provides personalized feedback and recommendations based on user performance
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from agents.adaptive_coach_agent import generate_adaptive_feedback

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
async def get_adaptive_feedback(request: Request, user_id: str):
    """
    Get personalized adaptive feedback for a user
    
    Analyzes:
    - Weak topics (< 60%) → recommends review
    - Strong topics (>= 80%) → builds on strengths
    - Recent activity → suggests next topics
    
    Returns:
    - Performance summary
    - Topics to review
    - New topic recommendations (via Google Gemini AI)
    - Motivational messages
    - Next steps
    """
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
