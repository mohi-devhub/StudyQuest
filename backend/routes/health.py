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
    
    # Check Gemini API
    gemini_status = await _check_gemini()
    health_status["dependencies"]["gemini"] = gemini_status
    
    if gemini_status["status"] != "healthy":
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


async def _check_gemini() -> Dict[str, Any]:
    """
    Check Google Gemini API availability.
    
    Returns:
        Dict with status, response time, and error if any
    """
    try:
        import google.generativeai as genai
        
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        
        if not gemini_api_key:
            return {
                "status": "unhealthy",
                "error": "GEMINI_API_KEY not configured"
            }
        
        start_time = time.time()
        
        # Configure and test Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(gemini_model)
        
        # Simple test generation
        response = model.generate_content("Hello")
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if response.text:
            return {
                "status": "healthy",
                "response_time_ms": response_time_ms
            }
        else:
            return {
                "status": "degraded",
                "response_time_ms": response_time_ms,
                "error": "Empty response"
            }
                
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
