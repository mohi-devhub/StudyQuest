"""
Quiz completion utilities - Handle quiz result storage and XP updates.

Functions:
- save_quiz_result: Store quiz results in Supabase
- update_user_xp: Update user's total XP and level
- update_topic_progress: Update progress for specific topic
- get_quiz_result: Retrieve quiz result by ID
"""

from datetime import datetime
from typing import Dict, Any, Optional
from supabase import Client


async def save_quiz_result(
    supabase: Client,
    user_id: str,
    topic: str,
    difficulty: str,
    score: float,
    total_questions: int,
    correct_answers: float,
    xp_gained: int,
    performance_feedback: str,
    next_difficulty: str,
    quiz_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Save quiz result to Supabase and update user progress.
    
    Args:
        supabase: Supabase client
        user_id: User ID
        topic: Quiz topic
        difficulty: Difficulty level (easy/medium/hard/expert)
        score: Percentage score (0-100)
        total_questions: Total number of questions
        correct_answers: Number of correct answers
        xp_gained: XP points earned
        performance_feedback: Feedback message
        next_difficulty: Recommended next difficulty
        quiz_data: Optional additional quiz data (questions, answers, etc.)
        
    Returns:
        Dictionary with quiz result ID and updated user stats
    """
    try:
        # 1. Insert quiz result into quiz_results table
        quiz_result = {
            "user_id": user_id,
            "topic": topic,
            "difficulty": difficulty,
            "score": score,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "xp_gained": xp_gained,
            "performance_feedback": performance_feedback,
            "next_difficulty": next_difficulty,
            "timestamp": datetime.utcnow().isoformat(),
            "quiz_data": quiz_data or {}
        }
        
        result = supabase.table("quiz_results").insert(quiz_result).execute()
        quiz_id = result.data[0]["id"]
        
        # 2. Update user XP and level
        xp_update = await update_user_xp(supabase, user_id, xp_gained)
        
        # 3. Update topic progress
        await update_topic_progress(
            supabase=supabase,
            user_id=user_id,
            topic=topic,
            score=score,
            difficulty=difficulty
        )
        
        # 4. Log XP gain
        await log_xp_gain(
            supabase=supabase,
            user_id=user_id,
            xp_amount=xp_gained,
            source="quiz_completion",
            topic=topic,
            details={
                "quiz_id": quiz_id,
                "score": score,
                "difficulty": difficulty
            }
        )
        
        return {
            "quiz_id": quiz_id,
            "user_id": user_id,
            "xp_gained": xp_gained,
            "total_xp": xp_update["total_xp"],
            "current_level": xp_update["current_level"],
            "level_up": xp_update.get("level_up", False),
            "timestamp": quiz_result["timestamp"]
        }
        
    except Exception as e:
        print(f"Error saving quiz result: {e}")
        raise


async def update_user_xp(
    supabase: Client,
    user_id: str,
    xp_gained: int
) -> Dict[str, Any]:
    """
    Update user's total XP and recalculate level.
    
    Args:
        supabase: Supabase client
        user_id: User ID
        xp_gained: XP points to add
        
    Returns:
        Dictionary with updated XP and level info
    """
    try:
        # Get current user stats
        user_response = supabase.table("users").select("total_xp, current_level").eq("user_id", user_id).execute()
        
        if not user_response.data:
            # Create new user record
            current_xp = 0
            current_level = 1
        else:
            current_xp = user_response.data[0].get("total_xp", 0)
            current_level = user_response.data[0].get("current_level", 1)
        
        # Calculate new XP and level
        new_xp = current_xp + xp_gained
        new_level = calculate_level(new_xp)
        level_up = new_level > current_level
        
        # Update user record
        update_data = {
            "user_id": user_id,
            "total_xp": new_xp,
            "current_level": new_level,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if not user_response.data:
            # Insert new user
            supabase.table("users").insert(update_data).execute()
        else:
            # Update existing user
            supabase.table("users").update(update_data).eq("user_id", user_id).execute()
        
        return {
            "total_xp": new_xp,
            "current_level": new_level,
            "level_up": level_up,
            "xp_for_next_level": (new_level * 500) - new_xp
        }
        
    except Exception as e:
        print(f"Error updating user XP: {e}")
        raise


def calculate_level(total_xp: int) -> int:
    """
    Calculate level from total XP.
    Formula: Level = floor(total_xp / 500) + 1
    
    Args:
        total_xp: Total XP earned
        
    Returns:
        Current level
    """
    return (total_xp // 500) + 1


async def update_topic_progress(
    supabase: Client,
    user_id: str,
    topic: str,
    score: float,
    difficulty: str
) -> Dict[str, Any]:
    """
    Update or create topic progress record with new quiz result.
    
    Args:
        supabase: Supabase client
        user_id: User ID
        topic: Topic name
        score: Quiz score (0-100)
        difficulty: Difficulty level
        
    Returns:
        Updated progress data
    """
    try:
        # Check if progress record exists
        progress_response = supabase.table("progress").select("*").eq(
            "user_id", user_id
        ).eq("topic", topic).execute()
        
        current_time = datetime.utcnow().isoformat()
        
        if not progress_response.data:
            # Create new progress record
            progress_data = {
                "user_id": user_id,
                "topic": topic,
                "avg_score": score,
                "total_attempts": 1,
                "last_attempt": current_time,
                "current_difficulty": difficulty,
                "best_score": score
            }
            result = supabase.table("progress").insert(progress_data).execute()
        else:
            # Update existing progress record
            existing = progress_response.data[0]
            total_attempts = existing.get("total_attempts", 0) + 1
            current_avg = existing.get("avg_score", 0)
            
            # Calculate new average score
            new_avg = ((current_avg * (total_attempts - 1)) + score) / total_attempts
            
            # Update best score if current score is higher
            best_score = max(existing.get("best_score", 0), score)
            
            update_data = {
                "avg_score": round(new_avg, 2),
                "total_attempts": total_attempts,
                "last_attempt": current_time,
                "current_difficulty": difficulty,
                "best_score": best_score
            }
            
            result = supabase.table("progress").update(update_data).eq(
                "user_id", user_id
            ).eq("topic", topic).execute()
        
        return result.data[0] if result.data else {}
        
    except Exception as e:
        print(f"Error updating topic progress: {e}")
        raise


async def log_xp_gain(
    supabase: Client,
    user_id: str,
    xp_amount: int,
    source: str,
    topic: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log XP gain event to xp_logs table.
    
    Args:
        supabase: Supabase client
        user_id: User ID
        xp_amount: XP gained
        source: Source of XP (quiz_completion, bonus, etc.)
        topic: Related topic
        details: Additional details
        
    Returns:
        Created log entry
    """
    try:
        log_entry = {
            "user_id": user_id,
            "xp_amount": xp_amount,
            "source": source,
            "topic": topic,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {}
        }
        
        result = supabase.table("xp_logs").insert(log_entry).execute()
        return result.data[0] if result.data else {}
        
    except Exception as e:
        print(f"Error logging XP gain: {e}")
        raise


async def get_quiz_result(
    supabase: Client,
    quiz_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve quiz result by ID.
    
    Args:
        supabase: Supabase client
        quiz_id: Quiz result ID
        
    Returns:
        Quiz result data or None if not found
    """
    try:
        result = supabase.table("quiz_results").select("*").eq("id", quiz_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error retrieving quiz result: {e}")
        return None


async def get_user_quiz_history(
    supabase: Client,
    user_id: str,
    limit: int = 10,
    topic: Optional[str] = None
) -> list[Dict[str, Any]]:
    """
    Get user's quiz history.
    
    Args:
        supabase: Supabase client
        user_id: User ID
        limit: Maximum number of results
        topic: Optional topic filter
        
    Returns:
        List of quiz results
    """
    try:
        query = supabase.table("quiz_results").select("*").eq("user_id", user_id)
        
        if topic:
            query = query.eq("topic", topic)
        
        result = query.order("timestamp", desc=True).limit(limit).execute()
        return result.data or []
    except Exception as e:
        print(f"Error retrieving quiz history: {e}")
        return []
