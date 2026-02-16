from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.supabase_client import get_admin_supabase
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
        admin_client = get_admin_supabase()
        token = credentials.credentials

        # Verify the token with the admin client (requires service_role key)
        user_response = admin_client.auth.get_user(token)
        
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


def validate_user_access(user_id: str, current_user: dict):
    """
    Verify the authenticated user matches the requested user_id.

    Raises:
        HTTPException: 403 if user_id does not match
    """
    if str(current_user.id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
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
