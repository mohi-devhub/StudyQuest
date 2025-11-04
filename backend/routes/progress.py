from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict
from utils.auth import get_current_user_id, verify_user

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
            "/progress/evaluate": "POST - Evaluate quiz answers and get progress report"
        }
    }


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
        
        return progress
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate quiz: {str(e)}"
        )

