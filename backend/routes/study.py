from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel, Field
from agents.research_agent import generate_notes, generate_notes_with_fallback
from agents.coach_agent import study_topic, study_multiple_topics
from agents.adaptive_quiz_agent import AdaptiveQuizAgent
from agents.recommendation_agent import RecommendationAgent
from utils.auth import verify_user, get_current_user_id
from utils.adaptive_quiz_utils import AdaptiveQuizHelper
from utils.recommendation_utils import RecommendationHelper
from utils.quiz_completion_utils import save_quiz_result, get_quiz_result
from utils.error_handlers import (
    validate_topic, 
    validate_num_questions,
    handle_api_timeout_error,
    handle_generation_error,
    get_fallback_message,
    ErrorResponse
)
from utils.cache_utils import get_cached_content, set_cached_content
from typing import List, Dict, Optional
import asyncio

# Import rate limiter
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix="/study",
    tags=["study"]
)


class GenerateNotesRequest(BaseModel):
    topic: str
    user_id: str = Field(None, description="User ID for tracking")
    use_cache: bool = Field(True, description="Use cached notes if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Data Structures",
                "user_id": "demo_user",
                "use_cache": True
            }
        }


class NotesResponse(BaseModel):
    topic: str
    summary: str
    key_points: List[str]
    examples: Optional[List[str]] = []
    tips: Optional[List[str]] = []
    
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
                ],
                "examples": [
                    "list_example = [1, 2, 3, 'four']",
                    "dict_example = {'name': 'John', 'age': 30}"
                ],
                "tips": [
                    "Use lists when order matters",
                    "Use dictionaries for key-value lookups"
                ]
            }
        }


class CompleteStudyRequest(BaseModel):
    """Request for complete study workflow (notes + quiz)"""
    topic: str = Field(..., min_length=1, max_length=50, description="Topic to study (max 50 chars)")
    num_questions: int = Field(5, ge=1, le=20, description="Number of quiz questions to generate")
    use_cache: bool = Field(True, description="Use cached content if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Python Decorators",
                "num_questions": 5,
                "use_cache": True
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


class AdaptiveQuizRequest(BaseModel):
    """Request for adaptive quiz generation"""
    topic: str = Field(..., min_length=1, max_length=200, description="Study topic")
    difficulty_preference: Optional[str] = Field(None, description="User's preferred difficulty (easy, medium, hard, expert)")
    num_questions: int = Field(5, ge=1, le=10, description="Number of questions (1-10)")
    notes: Optional[str] = Field(None, description="Optional study notes to use (if not provided, will be generated)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Machine Learning Algorithms",
                "difficulty_preference": "hard",
                "num_questions": 5
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
            "/study/adaptive-quiz": "POST - Generate adaptive quiz based on user performance",
            "/study/generate-notes": "POST - Generate only study notes",
            "/study/batch": "POST - Process multiple topics in parallel"
        },
        "adaptive_quiz": {
            "description": "Adaptive quiz adjusts difficulty based on past performance",
            "difficulty_levels": ["easy", "medium", "hard", "expert"],
            "logic": {
                "score_>_80%": "increase difficulty",
                "score_<_50%": "decrease difficulty",
                "user_preference": "overrides automatic adjustment"
            }
        }
    }


@router.post("/", response_model=StudyPackageResponse)
@limiter.limit("5/minute")
async def create_study_session(
    http_request: Request,
    request: CompleteStudyRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Create a complete study session with notes and quiz.
    
    This is the main endpoint for the frontend to use.
    Accepts a topic and generates:
    - Comprehensive study notes (summary + key points)
    - Quiz questions with answers and explanations
    
    Features:
    - Input validation (topic ≤ 50 chars)
    - Caching to reduce API calls
    - Graceful error handling with fallback messages
    - Timeout protection (30 seconds)
    
    Request:
    ```json
    {
        "topic": "Neural Networks",
        "num_questions": 5,
        "use_cache": true
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
            "num_questions": 5,
            "cached": false,
            "generation_time_ms": 2345
        }
    }
    ```
    
    Requires authentication.
    """
    import time
    start_time = time.time()
    
    try:
        # Validate inputs
        validated_topic = validate_topic(request.topic, max_length=50)
        validated_num_questions = validate_num_questions(request.num_questions, min_val=1, max_val=20)
        
        # Check cache first (if enabled)
        if request.use_cache:
            cached_content = await get_cached_content(
                topic=validated_topic,
                content_type='study_package',
                num_questions=validated_num_questions
            )
            
            if cached_content:
                # Return cached content with metadata
                cached_content['metadata']['cached'] = True
                cached_content['metadata']['cache_hit'] = True
                return cached_content
        
        # Generate new content with timeout protection
        try:
            study_package = await asyncio.wait_for(
                study_topic(
                    topic=validated_topic,
                    num_questions=validated_num_questions
                ),
                timeout=30.0  # 30 second timeout
            )
            
            # Add metadata
            generation_time_ms = int((time.time() - start_time) * 1000)
            study_package['metadata'] = study_package.get('metadata', {})
            study_package['metadata']['cached'] = False
            study_package['metadata']['generation_time_ms'] = generation_time_ms
            
            # Cache the result for future use
            await set_cached_content(
                topic=validated_topic,
                content_type='study_package',
                content=study_package,
                num_questions=validated_num_questions
            )
            
            return study_package
            
        except asyncio.TimeoutError:
            # Handle timeout gracefully
            fallback = get_fallback_message('study_package')
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
        # Re-raise HTTP exceptions as-is
        raise
        
    except ValueError as e:
        # Handle validation errors
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
        
    except Exception as e:
        # Handle unexpected errors
        print(f"Study package generation error: {str(e)}")
        fallback = get_fallback_message('study_package')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "message": fallback['message'],
                "code": "GENERATION_ERROR",
                "suggestion": fallback['suggestion']
            }
        )


@router.post("/retry", response_model=StudyPackageResponse)
@limiter.limit("5/minute")
async def retry_topic(
    http_request: Request,
    request: CompleteStudyRequest,
    current_user: dict = Depends(verify_user)
):
    """
    Retry a topic - regenerate notes and quiz for review.
    
    This endpoint:
    1. Regenerates study notes and quiz for the topic
    2. Records a "retry" event in xp_history
    3. Awards retry XP (10 XP per retry)
    
    Request:
    ```json
    {
        "topic": "Neural Networks",
        "num_questions": 5
    }
    ```
    
    Response: Same as /study endpoint, plus retry metadata
    
    Requires authentication via JWT token.
    """
    try:
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )
        
        # Get authenticated user ID
        user_id = current_user.id
        topic = request.topic.strip()
        
        # Generate new study package
        study_package = await study_topic(
            topic=topic,
            num_questions=request.num_questions
        )
        
        # Record retry event in xp_history with 10 XP
        from config.supabase_client import supabase
        
        retry_xp = 10
        
        # Get current user XP
        user_response = supabase.table('users').select('total_xp, level').eq('user_id', user_id).single().execute()
        current_xp = user_response.data.get('total_xp', 0) if user_response.data else 0
        new_xp = current_xp + retry_xp
        
        # Insert XP history record
        supabase.table('xp_history').insert({
            'user_id': user_id,
            'xp_change': retry_xp,
            'reason': f'retry',
            'topic': topic,
            'before_xp': current_xp,
            'after_xp': new_xp,
            'metadata': {
                'action': 'topic_retry',
                'topic': topic,
                'retry_xp': retry_xp
            }
        }).execute()
        
        # Update user's total XP
        supabase.table('users').update({
            'total_xp': new_xp,
            'level': new_xp // 500 + 1  # 500 XP per level
        }).eq('user_id', user_id).execute()
        
        # Add retry metadata to response
        study_package['metadata']['retry'] = True
        study_package['metadata']['xp_earned'] = retry_xp
        study_package['metadata']['total_xp'] = new_xp
        study_package['metadata']['level'] = new_xp // 500 + 1
        
        return study_package
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry topic: {str(e)}"
        )


@router.post("/generate-notes", response_model=NotesResponse)
@limiter.limit("5/minute")
async def create_study_notes(
    http_request: Request,
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
@limiter.limit("5/minute")
async def complete_study_workflow(
    http_request: Request,
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
@limiter.limit("5/minute")
async def batch_study_workflow(
    http_request: Request,
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


@router.post("/adaptive-quiz")
@limiter.limit("5/minute")
async def generate_adaptive_quiz(
    http_request: Request,
    request: AdaptiveQuizRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Generate an adaptive quiz based on user's past performance.
    
    This endpoint uses AI to adjust quiz difficulty based on:
    - User's average score on past quizzes
    - Past quiz difficulty levels
    - User's preferred difficulty (if specified)
    
    **Adaptive Logic**:
    - If average score > 80% → increase difficulty
    - If average score < 50% → decrease difficulty
    - Otherwise → maintain current difficulty
    - User preference always overrides automatic adjustment
    
    **Difficulty Levels**:
    - `easy`: Basic recall and understanding questions
    - `medium`: Application and analysis questions (default)
    - `hard`: Advanced synthesis and evaluation
    - `expert`: Complex problem-solving and critical thinking
    
    Request:
    ```json
    {
        "topic": "Machine Learning",
        "difficulty_preference": "hard",
        "num_questions": 5
    }
    ```
    
    Response includes:
    - Quiz questions at appropriate difficulty
    - Adaptive reasoning (why this difficulty was chosen)
    - User performance metrics
    - Difficulty recommendation
    
    Requires authentication.
    """
    try:
        # Validate topic
        if not request.topic or not request.topic.strip():
            raise HTTPException(
                status_code=400,
                detail="Topic cannot be empty"
            )
        
        topic = request.topic.strip()
        
        # Get adaptive quiz parameters based on user performance
        adaptive_params = await AdaptiveQuizHelper.get_adaptive_quiz_params(
            user_id=user_id,
            topic=topic,
            user_preference=request.difficulty_preference
        )
        
        # Get or generate study notes
        if request.notes:
            notes = request.notes
        else:
            # Generate notes for the topic
            print(f"Generating notes for topic: {topic}")
            notes_data = await generate_notes_with_fallback(topic)
            
            # Format notes for quiz generation
            notes = f"Topic: {notes_data['topic']}\n\n"
            notes += f"Summary: {notes_data['summary']}\n\n"
            notes += "Key Points:\n"
            for i, point in enumerate(notes_data['key_points'], 1):
                notes += f"{i}. {point}\n"
        
        # Generate adaptive quiz
        print(f"Generating {adaptive_params['difficulty']} difficulty quiz for {topic}")
        quiz_data = await AdaptiveQuizAgent.generate_adaptive_quiz_with_fallback(
            notes=notes,
            difficulty=adaptive_params['difficulty'],
            num_questions=request.num_questions,
            user_context=adaptive_params['user_performance']
        )
        
        # Format response with adaptive metadata
        response = AdaptiveQuizHelper.format_adaptive_response(
            quiz_data={
                'topic': topic,
                'questions': quiz_data['questions'],
                'metadata': quiz_data.get('metadata', {})
            },
            adaptive_params=adaptive_params
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate adaptive quiz: {str(e)}"
        )


@router.get("/recommendations")
@limiter.limit("5/minute")
async def get_study_recommendations(
    http_request: Request,
    user_id: str = Depends(get_current_user_id),
    max_recommendations: int = 5,
    include_ai_insights: bool = True
):
    """
    Get personalized study recommendations based on user progress.
    
    This endpoint analyzes:
    - **Weak Areas**: Topics with scores below 70%
    - **Stale Topics**: Topics not studied in 7+ days
    - **New Opportunities**: Topics not yet attempted
    
    **Recommendation Priority**:
    1. **High**: Weak areas (immediate improvement needed)
    2. **Medium**: Stale topics (prevent knowledge decay)
    3. **Low**: New topics (expand knowledge base)
    
    **XP Estimation**:
    - Calculated based on recommended difficulty and improvement potential
    - Weak areas earn bonus XP for improvement
    - Range: 120-225 XP per quiz
    
    **AI Insights** (if enabled):
    - Personalized motivational message
    - Learning pattern analysis
    - Specific advice for top priority
    
    Example Response:
    ```json
    {
      "recommendations": [
        {
          "topic": "Data Structures",
          "reason": "Improve performance (current: 62%, goal: 70%+)",
          "priority": "high",
          "category": "weak_area",
          "recommended_difficulty": "medium",
          "estimated_xp_gain": 180,
          "urgency": "Address gaps in understanding"
        }
      ],
      "ai_insights": {
        "motivational_message": "...",
        "learning_insight": "...",
        "priority_advice": "..."
      },
      "overall_stats": {
        "total_attempts": 25,
        "avg_score": 73.5,
        "topics_studied": 8
      }
    }
    ```
    
    Query Parameters:
    - `max_recommendations`: Maximum recommendations to return (default: 5)
    - `include_ai_insights`: Enable AI-generated insights (default: true)
    
    Requires authentication.
    """
    try:
        # Fetch user data
        recommendation_data = await RecommendationHelper.get_recommendation_data(user_id)
        
        if not recommendation_data['user_progress']:
            # New user with no progress
            return {
                'recommendations': [
                    {
                        'topic': 'Python Programming',
                        'reason': 'Great starting point for beginners',
                        'priority': 'high',
                        'category': 'new_learning',
                        'recommended_difficulty': 'easy',
                        'estimated_xp_gain': 120,
                        'urgency': 'Start your learning journey'
                    },
                    {
                        'topic': 'Web Development',
                        'reason': 'Popular and practical skill',
                        'priority': 'medium',
                        'category': 'new_learning',
                        'recommended_difficulty': 'easy',
                        'estimated_xp_gain': 120,
                        'urgency': 'Build foundational web skills'
                    }
                ],
                'ai_insights': {
                    'motivational_message': 'Welcome to StudyQuest! Start with the basics and build your knowledge step by step.',
                    'learning_insight': 'You\'re at the beginning of an exciting learning journey.',
                    'priority_advice': 'Start with Python Programming to build strong fundamentals.'
                },
                'overall_stats': {
                    'total_attempts': 0,
                    'avg_score': 0,
                    'topics_studied': 0
                },
                'metadata': {
                    'ai_enhanced': False,
                    'new_user': True
                }
            }
        
        # Generate recommendations
        recommendations_result = await RecommendationAgent.get_study_recommendations(
            user_progress=recommendation_data['user_progress'],
            all_available_topics=recommendation_data.get('all_available_topics'),
            max_recommendations=max_recommendations,
            include_ai_insights=include_ai_insights
        )
        
        # Format response
        response = RecommendationAgent.format_recommendation_response(recommendations_result)
        
        return response
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


class QuizCompletionRequest(BaseModel):
    """Request for completing a quiz and saving results"""
    user_id: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    difficulty: str = Field(..., pattern="^(easy|medium|hard|expert)$")
    score: float = Field(..., ge=0, le=100)
    total_questions: int = Field(..., ge=1)
    correct_answers: float = Field(..., ge=0)
    xp_gained: int = Field(..., ge=0)
    performance_feedback: str
    next_difficulty: str = Field(..., pattern="^(easy|medium|hard|expert)$")
    quiz_data: Optional[Dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "topic": "Python Programming",
                "difficulty": "medium",
                "score": 85,
                "total_questions": 10,
                "correct_answers": 8.5,
                "xp_gained": 165,
                "performance_feedback": "Great work! You're ready for harder challenges.",
                "next_difficulty": "hard",
                "quiz_data": {
                    "questions": [],
                    "user_answers": []
                }
            }
        }


class QuizCompletionResponse(BaseModel):
    """Response after quiz completion"""
    quiz_id: str
    user_id: str
    xp_gained: int
    total_xp: int
    current_level: int
    level_up: bool
    coach_feedback: Dict
    timestamp: str


class CoachFeedbackRequest(BaseModel):
    """Request for coach feedback"""
    topic: str
    difficulty: str
    score: float = Field(..., ge=0, le=100)
    correct_answers: int
    total_questions: int
    xp_gained: int
    next_difficulty: str
    context: Optional[str] = None


# DEPRECATED: Use /progress/v2/submit-quiz instead
# @router.post("/quiz/complete", response_model=QuizCompletionResponse)
# async def complete_quiz(
#     request: QuizCompletionRequest,
#     current_user: str = Depends(get_current_user_id)
# ):
#     """
#     Complete a quiz and save results to database.
#     
#     - Saves quiz result
#     - Updates user XP and level
#     - Updates topic progress
#     - Generates coach feedback
#     - Returns completion summary
#     """
#     raise HTTPException(
#         status_code=410,
#         detail="This endpoint is deprecated. Please use POST /progress/v2/submit-quiz instead."
#     )


# DEPRECATED: Coach feedback is now included in quiz submission response
# @router.post("/coach/feedback")
# async def get_coach_feedback(request: CoachFeedbackRequest):
#     """
#     Get motivational feedback from Coach Agent.
#     
#     - Analyzes quiz performance
#     - Generates personalized motivation
#     - Provides learning insights
#     - Suggests next steps
#     """
#     raise HTTPException(
#         status_code=410,
#         detail="This endpoint is deprecated. Coach feedback is included in quiz submission response."
#     )


@router.get("/quiz/result/{quiz_id}")
async def get_quiz_result_by_id(
    quiz_id: str,
    current_user: str = Depends(get_current_user_id)
):
    """
    Retrieve quiz result by ID.
    
    - Fetches quiz result from database
    - Includes all quiz details
    - Returns 404 if not found
    """
    try:
        from utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        result = await get_quiz_result(supabase, quiz_id)
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Quiz result not found"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve quiz result: {str(e)}"
        )


