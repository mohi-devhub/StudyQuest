"""
User Feedback Routes
Collects user feedback for beta testing and product improvement
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Supabase client
from config.supabase_client import supabase

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"]
)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class FeedbackSubmission(BaseModel):
    """Feedback submission from user"""
    user_id: str = Field(..., description="User ID")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 (poor) to 5 (excellent)")
    category: str = Field(default='general', description="ux, speed, accuracy, motivation, general")
    comments: Optional[str] = Field(None, max_length=1000, description="User comments")
    page_context: Optional[str] = Field(None, description="Page or feature being reviewed")
    session_metadata: Optional[Dict] = Field(default={}, description="Browser info, journey data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "demo_user",
                "rating": 5,
                "category": "ux",
                "comments": "The monochrome design is clean and focused. Love the terminal aesthetic!",
                "page_context": "dashboard",
                "session_metadata": {
                    "browser": "Chrome",
                    "screen_width": 1920
                }
            }
        }


class FeedbackResponse(BaseModel):
    """Response after feedback submission"""
    status: str
    message: str
    feedback_id: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Feedback received. Thank you for helping StudyQuest improve!",
                "feedback_id": "uuid-here"
            }
        }


class BetaTesterInfo(BaseModel):
    """Beta tester information"""
    user_id: str
    email: Optional[str]
    name: Optional[str]
    testing_status: str
    invited_at: datetime
    topics_studied: int
    quizzes_taken: int
    feedback_count: int


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/")
async def get_feedback_info():
    """Get information about feedback system"""
    return {
        "message": "StudyQuest Feedback System",
        "description": "Submit feedback to help us improve",
        "endpoints": {
            "POST /feedback/submit": "Submit user feedback",
            "GET /feedback/stats": "Get feedback statistics",
            "GET /feedback/recent": "Get recent feedback entries",
            "GET /feedback/beta-testers": "Get beta testing progress"
        },
        "categories": {
            "ux": "User Experience (clarity, design, ease of use)",
            "speed": "Performance and responsiveness",
            "accuracy": "Quiz quality and study content accuracy",
            "motivation": "Engagement and motivation to learn",
            "general": "General feedback and suggestions"
        },
        "rating_scale": {
            "5": "Excellent",
            "4": "Good",
            "3": "Okay",
            "2": "Poor",
            "1": "Very Poor"
        }
    }


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(submission: FeedbackSubmission):
    """
    Submit user feedback.
    
    Accepts ratings and comments about:
    - UX (user experience)
    - Speed (performance)
    - Accuracy (content quality)
    - Motivation (engagement)
    - General feedback
    
    Returns a thank you message and feedback ID.
    """
    try:
        # Validate category
        valid_categories = ['ux', 'speed', 'accuracy', 'motivation', 'general']
        if submission.category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": f"Invalid category. Must be one of: {', '.join(valid_categories)}",
                    "code": "INVALID_CATEGORY"
                }
            )
        
        # Insert feedback
        result = supabase.table('user_feedback').insert({
            'user_id': submission.user_id,
            'rating': submission.rating,
            'category': submission.category,
            'comments': submission.comments,
            'page_context': submission.page_context,
            'session_metadata': submission.session_metadata
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": "Failed to save feedback",
                    "code": "DATABASE_ERROR"
                }
            )
        
        feedback_id = result.data[0]['id']
        
        return {
            "status": "success",
            "message": "Feedback received. Thank you for helping StudyQuest improve!",
            "feedback_id": feedback_id
        }
        
    except HTTPException:
        raise
        
    except Exception as e:
        print(f"Feedback submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to submit feedback. Please try again.",
                "code": "SUBMISSION_ERROR"
            }
        )


@router.get("/stats")
async def get_feedback_stats():
    """
    Get feedback statistics.
    
    Returns:
    - Total feedback count
    - Average rating by category
    - Positive/negative breakdown
    - Recent trends
    """
    try:
        # Get summary from view
        summary = supabase.table('feedback_summary').select('*').execute()
        
        # Get overall stats
        all_feedback = supabase.table('user_feedback').select('rating, category, created_at').execute()
        
        if not all_feedback.data:
            return {
                "total_feedback": 0,
                "overall_rating": 0,
                "by_category": {},
                "rating_distribution": {},
                "recent_count_24h": 0
            }
        
        # Calculate rating distribution
        rating_dist = {}
        for i in range(1, 6):
            count = len([f for f in all_feedback.data if f['rating'] == i])
            rating_dist[str(i)] = count
        
        # Count recent feedback (last 24 hours)
        from datetime import timedelta
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_count = len([
            f for f in all_feedback.data 
            if datetime.fromisoformat(f['created_at'].replace('Z', '+00:00')) > recent_cutoff
        ])
        
        # Calculate overall rating
        overall_rating = sum(f['rating'] for f in all_feedback.data) / len(all_feedback.data)
        
        # Format category summary
        by_category = {}
        for cat in summary.data or []:
            by_category[cat['category']] = {
                'total_responses': cat['total_responses'],
                'avg_rating': float(cat['avg_rating']),
                'positive_count': cat['positive_count'],
                'negative_count': cat['negative_count']
            }
        
        return {
            "total_feedback": len(all_feedback.data),
            "overall_rating": round(overall_rating, 2),
            "by_category": by_category,
            "rating_distribution": rating_dist,
            "recent_count_24h": recent_count
        }
        
    except Exception as e:
        print(f"Feedback stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to retrieve feedback statistics",
                "code": "STATS_ERROR"
            }
        )


@router.get("/recent")
async def get_recent_feedback(limit: int = 10, category: Optional[str] = None):
    """
    Get recent feedback entries.
    
    Query params:
    - limit: Number of entries to return (default 10, max 50)
    - category: Filter by category (optional)
    """
    try:
        # Validate limit
        if limit < 1 or limit > 50:
            limit = 10
        
        # Build query
        query = supabase.table('user_feedback').select('*').order('created_at', desc=True).limit(limit)
        
        if category:
            query = query.eq('category', category)
        
        result = query.execute()
        
        return {
            "count": len(result.data or []),
            "feedback": result.data or []
        }
        
    except Exception as e:
        print(f"Recent feedback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to retrieve recent feedback",
                "code": "RETRIEVAL_ERROR"
            }
        )


@router.get("/beta-testers")
async def get_beta_testing_progress():
    """
    Get beta testing progress for all testers.
    
    Returns detailed statistics on:
    - Testing status
    - Topics studied
    - Quizzes completed
    - Feedback submitted
    """
    try:
        # Get progress from view
        result = supabase.table('beta_testing_progress').select('*').execute()
        
        return {
            "total_testers": len(result.data or []),
            "testers": result.data or []
        }
        
    except Exception as e:
        print(f"Beta testers error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to retrieve beta testing progress",
                "code": "RETRIEVAL_ERROR"
            }
        )


@router.get("/user/{user_id}")
async def get_user_feedback(user_id: str):
    """Get all feedback submitted by a specific user"""
    try:
        result = supabase.table('user_feedback').select('*').eq(
            'user_id', user_id
        ).order('created_at', desc=True).execute()
        
        return {
            "user_id": user_id,
            "total_feedback": len(result.data or []),
            "feedback": result.data or []
        }
        
    except Exception as e:
        print(f"User feedback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to retrieve user feedback",
                "code": "RETRIEVAL_ERROR"
            }
        )


@router.post("/beta-tester/register")
async def register_beta_tester(
    user_id: str,
    email: Optional[str] = None,
    name: Optional[str] = None
):
    """Register a new beta tester"""
    try:
        result = supabase.table('beta_testers').insert({
            'user_id': user_id,
            'email': email,
            'name': name,
            'testing_status': 'invited'
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": "error",
                    "message": "Failed to register beta tester",
                    "code": "REGISTRATION_ERROR"
                }
            )
        
        return {
            "status": "success",
            "message": f"Beta tester {name or user_id} registered successfully",
            "tester_id": result.data[0]['id']
        }
        
    except Exception as e:
        print(f"Beta tester registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": "Failed to register beta tester",
                "code": "REGISTRATION_ERROR"
            }
        )
