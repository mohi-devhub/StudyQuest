from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from agents.quiz_agent import generate_quiz, generate_quiz_with_fallback, generate_quiz_from_topic
from utils.auth import verify_user
from typing import List, Optional

router = APIRouter(
    prefix="/quiz",
    tags=["quiz"]
)


class GenerateQuizFromNotesRequest(BaseModel):
    notes: str
    num_questions: Optional[int] = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "notes": "Python functions are reusable blocks of code. They use the def keyword. Functions can take parameters and return values.",
                "num_questions": 5
            }
        }


class GenerateQuizFromTopicRequest(BaseModel):
    topic: str
    summary: str
    key_points: List[str]
    num_questions: Optional[int] = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Functions",
                "summary": "Functions are reusable blocks of code that perform specific tasks.",
                "key_points": [
                    "Functions are defined using the def keyword",
                    "They can accept parameters and return values",
                    "Functions promote code reusability"
                ],
                "num_questions": 5
            }
        }


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: List[QuizQuestion]
    total_questions: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "question": "What keyword is used to define a function in Python?",
                        "options": [
                            "A) function",
                            "B) def",
                            "C) func",
                            "D) define"
                        ],
                        "answer": "B",
                        "explanation": "The 'def' keyword is used to define functions in Python"
                    }
                ],
                "total_questions": 5
            }
        }


@router.get("/")
async def get_quizzes():
    """Get all quizzes"""
    return {"message": "Quizzes endpoint"}


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz_from_notes(
    request: GenerateQuizFromNotesRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Generate multiple-choice quiz questions from study notes.
    
    Creates 5 (or specified number of) unique multiple-choice questions
    based on the provided study material.
    
    Requires authentication.
    """
    try:
        if not request.notes or not request.notes.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Notes cannot be empty"
            )
        
        # Validate num_questions
        num_questions = request.num_questions or 5
        if num_questions < 1 or num_questions > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of questions must be between 1 and 20"
            )
        
        # Generate quiz using the quiz agent with fallback
        questions = await generate_quiz_with_fallback(
            request.notes.strip(),
            num_questions
        )
        
        return {
            "questions": questions,
            "total_questions": len(questions)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )


@router.post("/generate-from-topic", response_model=QuizResponse)
async def generate_quiz_from_structured_notes(
    request: GenerateQuizFromTopicRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Generate multiple-choice quiz questions from structured notes.
    
    Creates quiz questions from a topic, summary, and key points.
    This is useful when you already have structured study notes.
    
    Requires authentication.
    """
    try:
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )
        
        if not request.key_points or len(request.key_points) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Key points cannot be empty"
            )
        
        # Validate num_questions
        num_questions = request.num_questions or 5
        if num_questions < 1 or num_questions > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Number of questions must be between 1 and 20"
            )
        
        # Generate quiz from structured notes
        questions = await generate_quiz_from_topic(
            topic=request.topic.strip(),
            summary=request.summary.strip(),
            key_points=request.key_points,
            num_questions=num_questions
        )
        
        return {
            "questions": questions,
            "total_questions": len(questions)
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

