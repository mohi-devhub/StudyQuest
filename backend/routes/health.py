from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
import httpx
import os
import time
from config.supabase_client import get_supabase

router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dict with status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with dependency status.
    
    Checks:
    - Supabase database connectivity
    - OpenRouter API availability
    
    Returns:
        Dict with overall status and individual dependency statuses
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": {}
    }
    
    # Check Supabase connection
    supabase_status = await _check_supabase()
    health_status["dependencies"]["supabase"] = supabase_status
    
    if supabase_status["status"] != "healthy":
        health_status["status"] = "degraded"
    
    # Check OpenRouter API
    openrouter_status = await _check_openrouter()
    health_status["dependencies"]["openrouter"] = openrouter_status
    
    if openrouter_status["status"] != "healthy":
        health_status["status"] = "degraded"
    
    return health_status


async def _check_supabase() -> Dict[str, Any]:
    """
    Check Supabase database connectivity.
    
    Returns:
        Dict with status, response time, and error if any
    """
    try:
        supabase = get_supabase()
        start_time = time.time()
        
        # Simple query to check connectivity
        result = supabase.table('users').select('user_id').limit(1).execute()
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "status": "healthy",
            "response_time_ms": response_time_ms
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


async def _check_openrouter() -> Dict[str, Any]:
    """
    Check OpenRouter API availability.
    
    Returns:
        Dict with status, response time, and error if any
    """
    try:
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        
        if not openrouter_api_key:
            return {
                "status": "unhealthy",
                "error": "OPENROUTER_API_KEY not configured"
            }
        
        start_time = time.time()
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={
                    "Authorization": f"Bearer {openrouter_api_key}"
                }
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": response_time_ms
                }
            else:
                return {
                    "status": "degraded",
                    "response_time_ms": response_time_ms,
                    "error": f"HTTP {response.status_code}"
                }
                
    except httpx.TimeoutException:
        return {
            "status": "unhealthy",
            "error": "Request timeout (>5s)"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
