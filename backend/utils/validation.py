"""
Input Validation Utility
Provides validation functions for user inputs to prevent injection attacks and ensure data integrity
"""
import re
from typing import Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
import uuid


class ValidationError(Exception):
    """Custom validation error"""
    pass


def validate_topic_name(topic: str, max_length: int = 200) -> str:
    """
    Validate topic name
    
    Rules:
    - Max length: 200 characters (configurable)
    - Allowed: alphanumeric, spaces, hyphens, underscores, periods, commas
    - Not allowed: special characters that could be used for injection
    
    Args:
        topic: Topic name to validate
        max_length: Maximum allowed length
        
    Returns:
        str: Validated and sanitized topic name
        
    Raises:
        ValidationError: If validation fails
    """
    if not topic or not topic.strip():
        raise ValidationError("Topic name cannot be empty")
    
    topic = topic.strip()
    
    if len(topic) > max_length:
        raise ValidationError(f"Topic name cannot exceed {max_length} characters")
    
    # Allow alphanumeric, spaces, and common punctuation
    # Block special characters that could be used for injection
    pattern = r'^[a-zA-Z0-9\s\-_.,()\'\"]+$'
    
    if not re.match(pattern, topic):
        raise ValidationError(
            "Topic name contains invalid characters. "
            "Only letters, numbers, spaces, and basic punctuation are allowed."
        )
    
    return topic


def validate_user_id(user_id: str) -> str:
    """
    Validate user ID (UUID format)
    
    Args:
        user_id: User ID to validate
        
    Returns:
        str: Validated user ID
        
    Raises:
        ValidationError: If validation fails
    """
    if not user_id or not user_id.strip():
        raise ValidationError("User ID cannot be empty")
    
    user_id = user_id.strip()
    
    # Check if it's a valid UUID format
    try:
        uuid.UUID(user_id)
        return user_id
    except ValueError:
        # If not UUID, check if it's alphanumeric (for demo users)
        if re.match(r'^[a-zA-Z0-9_-]+$', user_id) and len(user_id) <= 50:
            return user_id
        raise ValidationError("Invalid user ID format")


def validate_difficulty(difficulty: str) -> str:
    """
    Validate difficulty level
    
    Args:
        difficulty: Difficulty level to validate
        
    Returns:
        str: Validated difficulty level
        
    Raises:
        ValidationError: If validation fails
    """
    valid_difficulties = ['easy', 'medium', 'hard', 'expert']
    
    if not difficulty:
        return 'medium'  # Default
    
    difficulty = difficulty.lower().strip()
    
    if difficulty not in valid_difficulties:
        raise ValidationError(
            f"Invalid difficulty level. Must be one of: {', '.join(valid_difficulties)}"
        )
    
    return difficulty


def validate_num_questions(num_questions: int, min_val: int = 1, max_val: int = 20) -> int:
    """
    Validate number of questions
    
    Args:
        num_questions: Number of questions to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        int: Validated number of questions
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(num_questions, int):
        try:
            num_questions = int(num_questions)
        except (ValueError, TypeError):
            raise ValidationError("Number of questions must be an integer")
    
    if num_questions < min_val or num_questions > max_val:
        raise ValidationError(
            f"Number of questions must be between {min_val} and {max_val}"
        )
    
    return num_questions


def validate_score(score: float) -> float:
    """
    Validate quiz score
    
    Args:
        score: Score to validate (0-100)
        
    Returns:
        float: Validated score
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(score, (int, float)):
        try:
            score = float(score)
        except (ValueError, TypeError):
            raise ValidationError("Score must be a number")
    
    if score < 0 or score > 100:
        raise ValidationError("Score must be between 0 and 100")
    
    return score


def sanitize_text_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input to prevent injection attacks
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized text
        
    Raises:
        ValidationError: If validation fails
    """
    if not text:
        raise ValidationError("Text input cannot be empty")
    
    text = text.strip()
    
    if len(text) > max_length:
        raise ValidationError(f"Text input cannot exceed {max_length} characters")
    
    # Remove potentially dangerous characters
    # Keep alphanumeric, spaces, and common punctuation
    # This is a basic sanitization - adjust based on your needs
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'on\w+\s*=',  # Event handlers
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text


async def validate_request_size(request: Request, max_size_kb: int = 10):
    """
    Middleware to validate request body size
    
    Args:
        request: FastAPI request object
        max_size_kb: Maximum allowed size in KB
        
    Raises:
        HTTPException: If request is too large
    """
    content_length = request.headers.get('content-length')
    
    if content_length:
        content_length = int(content_length)
        max_size_bytes = max_size_kb * 1024
        
        if content_length > max_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Maximum size: {max_size_kb}KB"
            )


def validate_email(email: str) -> str:
    """
    Validate email format
    
    Args:
        email: Email to validate
        
    Returns:
        str: Validated email
        
    Raises:
        ValidationError: If validation fails
    """
    if not email or not email.strip():
        raise ValidationError("Email cannot be empty")
    
    email = email.strip().lower()
    
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email address too long")
    
    return email


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password too long (max 128 characters)"
    
    # Check for at least one uppercase, one lowercase, and one digit
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    return True, "Password is strong"


# Validation decorator for routes
def validate_input(
    topic_field: Optional[str] = None,
    user_id_field: Optional[str] = None,
    max_request_size_kb: int = 10
):
    """
    Decorator to validate input fields
    
    Usage:
        @validate_input(topic_field='topic', user_id_field='user_id')
        async def my_endpoint(request: MyRequest):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get request object from kwargs
            request_obj = kwargs.get('request')
            
            if request_obj:
                # Validate topic if specified
                if topic_field and hasattr(request_obj, topic_field):
                    topic = getattr(request_obj, topic_field)
                    try:
                        validated_topic = validate_topic_name(topic)
                        setattr(request_obj, topic_field, validated_topic)
                    except ValidationError as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e)
                        )
                
                # Validate user_id if specified
                if user_id_field and hasattr(request_obj, user_id_field):
                    user_id = getattr(request_obj, user_id_field)
                    try:
                        validated_user_id = validate_user_id(user_id)
                        setattr(request_obj, user_id_field, validated_user_id)
                    except ValidationError as e:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e)
                        )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
