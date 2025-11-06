"""
Standardized Error Responses and Validation Utilities
"""
from fastapi import HTTPException, status
from pydantic import BaseModel, validator
from typing import Optional, Any
import re


# ============================================================================
# STANDARDIZED ERROR RESPONSE MODEL
# ============================================================================

class ErrorResponse(BaseModel):
    """Standardized error response format"""
    status: str = "error"
    message: str
    code: Optional[str] = None
    details: Optional[Any] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "Unable to generate quiz. Try again later.",
                "code": "API_TIMEOUT",
                "details": None
            }
        }


class SuccessResponse(BaseModel):
    """Standardized success response format"""
    status: str = "success"
    data: Any
    message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {"topic": "Python", "notes": "..."},
                "message": "Study package generated successfully"
            }
        }


# ============================================================================
# VALIDATION UTILITIES
# ============================================================================

def validate_topic(topic: str, max_length: int = 50) -> str:
    """
    Validate topic input.
    
    Rules:
    - Cannot be empty or only whitespace
    - Max length: 50 characters (default)
    - Must contain at least one alphanumeric character
    - Remove leading/trailing whitespace
    
    Args:
        topic: Topic string to validate
        max_length: Maximum allowed length
        
    Returns:
        Cleaned topic string
        
    Raises:
        HTTPException: If validation fails
    """
    if not topic or not topic.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic cannot be empty"
        )
    
    cleaned_topic = topic.strip()
    
    if len(cleaned_topic) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Topic cannot exceed {max_length} characters"
        )
    
    # Must contain at least one alphanumeric character
    if not re.search(r'[a-zA-Z0-9]', cleaned_topic):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Topic must contain at least one letter or number"
        )
    
    return cleaned_topic


def validate_num_questions(num_questions: int, min_val: int = 1, max_val: int = 20) -> int:
    """
    Validate number of questions.
    
    Args:
        num_questions: Number of questions
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Validated number
        
    Raises:
        HTTPException: If validation fails
    """
    if num_questions < min_val or num_questions > max_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of questions must be between {min_val} and {max_val}"
        )
    return num_questions


def validate_difficulty(difficulty: str) -> str:
    """
    Validate difficulty level.
    
    Args:
        difficulty: Difficulty string
        
    Returns:
        Lowercase difficulty string
        
    Raises:
        HTTPException: If invalid difficulty
    """
    valid_difficulties = ['easy', 'medium', 'hard', 'expert']
    difficulty_lower = difficulty.lower().strip()
    
    if difficulty_lower not in valid_difficulties:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Difficulty must be one of: {', '.join(valid_difficulties)}"
        )
    
    return difficulty_lower


# ============================================================================
# ERROR HANDLERS
# ============================================================================

def handle_api_timeout_error(operation: str = "API request") -> HTTPException:
    """Return standardized timeout error"""
    return HTTPException(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        detail={
            "status": "error",
            "message": f"Request timeout. The {operation} took too long. Please try again.",
            "code": "API_TIMEOUT"
        }
    )


def handle_generation_error(resource: str = "content") -> HTTPException:
    """Return standardized generation error"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "status": "error",
            "message": f"Unable to generate {resource}. Please try again later.",
            "code": "GENERATION_ERROR"
        }
    )


def handle_validation_error(message: str) -> HTTPException:
    """Return standardized validation error"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "status": "error",
            "message": message,
            "code": "VALIDATION_ERROR"
        }
    )


def handle_database_error(operation: str = "database operation") -> HTTPException:
    """Return standardized database error"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "status": "error",
            "message": f"Database error during {operation}. Please try again.",
            "code": "DATABASE_ERROR"
        }
    )


def handle_not_found_error(resource: str) -> HTTPException:
    """Return standardized not found error"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "status": "error",
            "message": f"{resource} not found",
            "code": "NOT_FOUND"
        }
    )


# ============================================================================
# FALLBACK MESSAGES
# ============================================================================

FALLBACK_MESSAGES = {
    "quiz": {
        "message": "Unable to generate quiz questions at this time.",
        "suggestion": "Please try again in a few moments or choose a different topic."
    },
    "notes": {
        "message": "Unable to generate study notes at this time.",
        "suggestion": "Please try again in a few moments or refine your topic."
    },
    "study_package": {
        "message": "Unable to generate complete study package at this time.",
        "suggestion": "Please try again later or contact support if the issue persists."
    },
    "coach_feedback": {
        "message": "Unable to generate coach feedback at this time.",
        "suggestion": "Your quiz results have been saved. Feedback will be available shortly."
    }
}


def get_fallback_message(resource_type: str) -> dict:
    """Get fallback message for a resource type"""
    return FALLBACK_MESSAGES.get(resource_type, {
        "message": "Service temporarily unavailable.",
        "suggestion": "Please try again later."
    })
