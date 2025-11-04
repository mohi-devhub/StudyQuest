from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from agents.research_agent import generate_notes, generate_notes_with_fallback
from agents.coach_agent import study_topic, study_multiple_topics
from utils.auth import verify_user
from typing import List, Dict

router = APIRouter(
    prefix="/study",
    tags=["study"]
)


class GenerateNotesRequest(BaseModel):
    topic: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Data Structures"
            }
        }


class NotesResponse(BaseModel):
    topic: str
    summary: str
    key_points: List[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Data Structures",
                "summary": "Python provides built-in data structures like lists, tuples, dictionaries, and sets to organize and store data efficiently.",
                "key_points": [
                    "Lists are ordered, mutable collections that can hold items of different types",
                    "Tuples are immutable sequences, useful for fixed collections of items",
                    "Dictionaries store key-value pairs for fast lookups",
                    "Sets are unordered collections of unique elements",
                    "Each data structure has specific use cases and performance characteristics"
                ]
            }
        }


class CompleteStudyRequest(BaseModel):
    """Request for complete study workflow (notes + quiz)"""
    topic: str = Field(..., min_length=1, max_length=200)
    num_questions: int = Field(5, ge=1, le=20, description="Number of quiz questions to generate")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Decorators",
                "num_questions": 5
            }
        }


class StudyPackageResponse(BaseModel):
    """Complete study package with notes and quiz"""
    topic: str
    notes: Dict
    quiz: List[Dict]
    metadata: Dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Decorators",
                "notes": {
                    "topic": "Python Decorators",
                    "summary": "Decorators are a powerful feature...",
                    "key_points": ["...", "..."]
                },
                "quiz": [
                    {
                        "question": "What is a decorator in Python?",
                        "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
                        "answer": "B",
                        "explanation": "..."
                    }
                ],
                "metadata": {
                    "num_key_points": 7,
                    "num_questions": 5
                }
            }
        }


class BatchStudyRequest(BaseModel):
    """Request for studying multiple topics"""
    topics: List[str] = Field(..., min_items=1, max_items=10)
    num_questions: int = Field(3, ge=1, le=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "topics": ["REST API", "GraphQL", "WebSockets"],
                "num_questions": 3
            }
        }


@router.get("/")
async def get_study_info():
    """
    Get information about study endpoints
    """
    return {
        "message": "Study endpoints for generating notes and quizzes",
        "endpoints": {
            "/study": "POST - Generate complete study package (notes + quiz)",
            "/study/complete": "POST - Same as /study (alternative endpoint)",
            "/study/generate-notes": "POST - Generate only study notes",
            "/study/batch": "POST - Process multiple topics in parallel"
        }
    }


@router.post("/", response_model=StudyPackageResponse)
async def create_study_session(
    request: CompleteStudyRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Create a complete study session with notes and quiz.
    
    This is the main endpoint for the frontend to use.
    Accepts a topic and generates:
    - Comprehensive study notes (summary + key points)
    - Quiz questions with answers and explanations
    
    Request:
    ```json
    {
        "topic": "Neural Networks",
        "num_questions": 5
    }
    ```
    
    Response:
    ```json
    {
        "topic": "Neural Networks",
        "notes": {
            "topic": "Neural Networks",
            "summary": "...",
            "key_points": ["...", "..."]
        },
        "quiz": [
            {
                "question": "What is a neural network?",
                "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
                "answer": "B",
                "explanation": "..."
            }
        ],
        "metadata": {
            "num_key_points": 7,
            "num_questions": 5
        }
    }
    ```
    
    Requires authentication.
    """
    try:
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )
        
        # Use Coach Agent to coordinate the complete workflow
        study_package = await study_topic(
            topic=request.topic.strip(),
            num_questions=request.num_questions
        )
        
        return study_package
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study package: {str(e)}"
        )


@router.post("/generate-notes", response_model=NotesResponse)
async def create_study_notes(
    request: GenerateNotesRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Generate AI-powered study notes for a given topic.
    
    Uses OpenRouter API with Llama or Mixtral models to create
    beginner-friendly summaries and key points.
    
    Requires authentication.
    """
    try:
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )
        
        # Generate notes using the research agent with fallback
        notes = await generate_notes_with_fallback(request.topic.strip())
        
        return notes
        
    except ValueError as e:
        # API key not configured
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server configuration error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate notes: {str(e)}"
        )


@router.post("/complete", response_model=StudyPackageResponse)
async def complete_study_workflow(
    request: CompleteStudyRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Complete study workflow: Generate notes AND quiz in one request.
    
    This endpoint uses the Coach Agent to:
    1. Generate comprehensive study notes
    2. Create quiz questions from those notes
    3. Return a complete study package
    
    This is more efficient than calling /generate-notes and /generate-quiz separately.
    
    Requires authentication.
    """
    try:
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )
        
        # Use Coach Agent to coordinate the complete workflow
        study_package = await study_topic(
            topic=request.topic.strip(),
            num_questions=request.num_questions
        )
        
        return study_package
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study package: {str(e)}"
        )


@router.post("/batch", response_model=List[StudyPackageResponse])
async def batch_study_workflow(
    request: BatchStudyRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Study multiple topics in parallel.
    
    Generates complete study packages for multiple topics simultaneously.
    More efficient than calling /complete multiple times sequentially.
    
    Note: Free tier API rate limits may apply with many topics.
    
    Requires authentication.
    """
    try:
        if not request.topics or len(request.topics) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topics list cannot be empty"
            )
        
        # Validate each topic
        for topic in request.topics:
            if not topic or not topic.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="All topics must be non-empty strings"
                )
        
        # Use Coach Agent to process multiple topics in parallel
        study_packages = await study_multiple_topics(
            topics=[t.strip() for t in request.topics],
            num_questions=request.num_questions
        )
        
        return study_packages
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate study packages: {str(e)}"
        )

