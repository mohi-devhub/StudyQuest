from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.supabase_client import get_supabase
from typing import Optional

security = HTTPBearer()


async def verify_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verify Supabase JWT token and return user data.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        dict: User data from Supabase
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        supabase = get_supabase()
        token = credentials.credentials
        
        # Verify the token with Supabase
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_response.user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(user: dict = Depends(verify_user)) -> str:
    """
    Extract user ID from verified user data.
    
    Args:
        user: Verified user data from verify_user dependency
        
    Returns:
        str: User ID
    """
    return user.id
