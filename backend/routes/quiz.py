from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from agents.quiz_agent import generate_quiz, generate_quiz_with_fallback, generate_quiz_from_topic
from utils.auth import verify_user
from utils.error_handlers import (
    validate_topic,
    validate_num_questions,
    handle_api_timeout_error,
    handle_generation_error,
    get_fallback_message,
    ErrorResponse
)
from utils.cache_utils import get_cached_content, set_cached_content
from typing import List, Optional
import asyncio
import time

# Import rate limiter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

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
    topic: str = Field(..., min_length=1, max_length=50, description="Topic name (max 50 chars)")
    summary: str = Field(..., min_length=10, description="Topic summary")
    key_points: List[str] = Field(..., min_items=1, description="Key points about the topic")
    num_questions: Optional[int] = Field(5, ge=1, le=20, description="Number of questions")
    use_cache: bool = Field(True, description="Use cached quiz if available")
    
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
                "num_questions": 5,
                "use_cache": True
            }
        }


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    answer: str
    explanation: Optional[str] = ""


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


class SimpleQuizRequest(BaseModel):
    """Simple quiz generation request"""
    topic: str = Field(..., min_length=1, max_length=50, description="Topic name (max 50 chars)")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, or hard")
    user_id: Optional[str] = Field(None, description="User ID for tracking (optional, extracted from auth token)")
    use_cache: bool = Field(True, description="Use cached quiz if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Functions",
                "num_questions": 5,
                "difficulty": "medium",
                "use_cache": True
            }
        }


class SimpleQuizResponse(BaseModel):
    """Simple quiz response"""
    topic: str
    quiz: List[QuizQuestion]
    metadata: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Functions",
                "quiz": [
                    {
                        "question": "What keyword is used to define a function in Python?",
                        "options": ["A) function", "B) def", "C) func", "D) define"],
                        "answer": "B",
                        "explanation": "The 'def' keyword is used to define functions in Python"
                    }
                ],
                "metadata": {
                    "num_questions": 5,
                    "difficulty": "medium",
                    "cached": False,
                    "generation_time_ms": 3500
                }
            }
        }


@router.post("/", response_model=SimpleQuizResponse)
@limiter.limit("5/minute")
async def generate_simple_quiz(
    http_request: Request,
    request: SimpleQuizRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Generate a quiz directly from a topic (simplified endpoint for frontend).
    
    This endpoint:
    1. Generates study notes internally
    2. Creates quiz questions from those notes
    3. Returns just the quiz (not the notes)
    
    Features:
    - Input validation (topic ≤ 50 chars)
    - Difficulty support (easy, medium, hard)
    - Caching to reduce API calls
    - Timeout protection (25 seconds)
    - Graceful error handling
    
    Requires authentication.
    """
    from agents.coach_agent import study_topic
    
    start_time = time.time()
    
    try:
        # Validate inputs
        validated_topic = validate_topic(request.topic, max_length=50)
        validated_num_questions = validate_num_questions(request.num_questions, min_val=1, max_val=20)
        
        # Validate difficulty
        valid_difficulties = ['easy', 'medium', 'hard']
        difficulty = request.difficulty.lower()
        if difficulty not in valid_difficulties:
            difficulty = 'medium'
        
        # Check cache first (if enabled)
        cache_key_suffix = f"_{difficulty}"  # Different cache for each difficulty
        if request.use_cache:
            cached_quiz = await get_cached_content(
                topic=validated_topic + cache_key_suffix,
                content_type='quiz_only',
                num_questions=validated_num_questions
            )
            
            if cached_quiz:
                return {
                    "topic": validated_topic,
                    "quiz": cached_quiz.get('quiz', []),
                    "metadata": {
                        "num_questions": len(cached_quiz.get('quiz', [])),
                        "difficulty": difficulty,
                        "cached": True,
                        "cache_hit": True
                    }
                }
        
        # Generate study package (notes + quiz) with timeout protection
        try:
            study_package = await asyncio.wait_for(
                study_topic(
                    topic=validated_topic,
                    num_questions=validated_num_questions
                ),
                timeout=25.0  # 25 second timeout
            )
            
            # Extract just the quiz
            quiz = study_package.get('quiz', [])
            
            if not quiz or len(quiz) == 0:
                raise ValueError("No quiz questions generated")
            
            # Add metadata
            generation_time_ms = int((time.time() - start_time) * 1000)
            metadata = {
                "num_questions": len(quiz),
                "difficulty": difficulty,
                "cached": False,
                "generation_time_ms": generation_time_ms
            }
            
            # Cache the result
            quiz_data = {"quiz": quiz}
            await set_cached_content(
                topic=validated_topic + cache_key_suffix,
                content_type='quiz_only',
                content=quiz_data,
                num_questions=validated_num_questions
            )
            
            return {
                "topic": validated_topic,
                "quiz": quiz,
                "metadata": metadata
            }
            
        except asyncio.TimeoutError:
            fallback = get_fallback_message('quiz')
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "status": "error",
                    "message": fallback['message'],
                    "code": "API_TIMEOUT",
                    "suggestion": fallback['suggestion']
                }
            )
        
    except HTTPException:
        raise
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Simple quiz generation error: {str(e)}")
        print(f"Traceback: {error_trace}")
        fallback = get_fallback_message('quiz')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": f"{fallback['message']} Error: {str(e)}",
                "code": "GENERATION_ERROR",
                "suggestion": fallback['suggestion']
            }
        )


@router.post("/generate", response_model=QuizResponse)
@limiter.limit("5/minute")
async def generate_quiz_from_notes(
    http_request: Request,
    request: GenerateQuizFromNotesRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Generate multiple-choice quiz questions from study notes.
    
    Creates quiz questions based on the provided study material with:
    - Input validation
    - Graceful error handling
    - Timeout protection (20 seconds)
    
    Requires authentication.
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        if not request.notes or not request.notes.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Notes cannot be empty",
                    "code": "VALIDATION_ERROR"
                }
            )
        
        # Validate num_questions
        num_questions = validate_num_questions(request.num_questions or 5, min_val=1, max_val=20)
        
        # Generate quiz with timeout protection
        try:
            questions = await asyncio.wait_for(
                generate_quiz_with_fallback(
                    request.notes.strip(),
                    num_questions
                ),
                timeout=20.0  # 20 second timeout
            )
            
            return {
                "questions": questions,
                "total_questions": len(questions)
            }
            
        except asyncio.TimeoutError:
            fallback = get_fallback_message('quiz')
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "status": "error",
                    "message": fallback['message'],
                    "code": "API_TIMEOUT",
                    "suggestion": fallback['suggestion']
                }
            )
        
    except HTTPException:
        raise
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
        
    except Exception as e:
        print(f"Quiz generation error: {str(e)}")
        fallback = get_fallback_message('quiz')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": fallback['message'],
                "code": "GENERATION_ERROR",
                "suggestion": fallback['suggestion']
            }
        )


@router.post("/generate-from-topic", response_model=QuizResponse)
@limiter.limit("5/minute")
async def generate_quiz_from_structured_notes(
    http_request: Request,
    request: GenerateQuizFromTopicRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Generate multiple-choice quiz questions from structured notes.
    
    Creates quiz questions from a topic, summary, and key points with:
    - Input validation (topic ≤ 50 chars)
    - Caching support
    - Graceful error handling
    - Timeout protection (20 seconds)
    
    Requires authentication.
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        validated_topic = validate_topic(request.topic, max_length=50)
        
        if not request.key_points or len(request.key_points) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "Key points cannot be empty",
                    "code": "VALIDATION_ERROR"
                }
            )
        
        num_questions = validate_num_questions(request.num_questions or 5, min_val=1, max_val=20)
        
        # Check cache first (if enabled)
        if request.use_cache:
            cached_quiz = await get_cached_content(
                topic=validated_topic,
                content_type='quiz',
                num_questions=num_questions
            )
            
            if cached_quiz:
                return {
                    "questions": cached_quiz.get('questions', []),
                    "total_questions": len(cached_quiz.get('questions', []))
                }
        
        # Generate quiz with timeout protection
        try:
            questions = await asyncio.wait_for(
                generate_quiz_from_topic(
                    topic=validated_topic,
                    summary=request.summary.strip(),
                    key_points=request.key_points,
                    num_questions=num_questions
                ),
                timeout=20.0  # 20 second timeout
            )
            
            # Cache the result
            quiz_data = {"questions": questions}
            await set_cached_content(
                topic=validated_topic,
                content_type='quiz',
                content=quiz_data,
                num_questions=num_questions
            )
            
            return {
                "questions": questions,
                "total_questions": len(questions)
            }
            
        except asyncio.TimeoutError:
            fallback = get_fallback_message('quiz')
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "status": "error",
                    "message": fallback['message'],
                    "code": "API_TIMEOUT",
                    "suggestion": fallback['suggestion']
                }
            )
        
    except HTTPException:
        raise
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
        
    except Exception as e:
        print(f"Quiz generation error: {str(e)}")
        fallback = get_fallback_message('quiz')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": fallback['message'],
                "code": "GENERATION_ERROR",
                "suggestion": fallback['suggestion']
            }
        )

