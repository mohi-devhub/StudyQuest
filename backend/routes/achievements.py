"""
Badges & Achievements Routes
Handles badge unlocking, milestone tracking, and achievement display
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# Supabase client
from config.supabase_client import supabase

router = APIRouter(
    prefix="/achievements",
    tags=["achievements"]
)


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class Badge(BaseModel):
    """Badge information"""
    id: str
    badge_key: str
    name: str
    description: str
    category: str
    symbol: str
    tier: int
    requirement_type: str
    requirement_value: int


class UnlockedBadge(BaseModel):
    """User's unlocked badge"""
    badge_id: str
    name: str
    description: str
    symbol: str
    tier: int
    unlocked_at: datetime
    seen: bool


class Milestone(BaseModel):
    """Milestone definition"""
    id: str
    milestone_key: str
    name: str
    description: str
    category: str
    threshold: int
    symbol: str


class UserAchievements(BaseModel):
    """Complete user achievements"""
    total_badges: int
    bronze_badges: int
    silver_badges: int
    gold_badges: int
    platinum_badges: int
    total_milestones: int
    latest_badge_at: Optional[datetime]


# ============================================================================
# ROUTES
# ============================================================================

@router.get("/")
async def get_achievements_info():
    """Information about achievements system"""
    return {
        "message": "Badge & Milestone Achievement System",
        "endpoints": {
            "GET /all-badges": "Get list of all available badges",
            "GET /user/{user_id}/badges": "Get user's unlocked badges",
            "GET /user/{user_id}/summary": "Get achievement summary",
            "POST /user/{user_id}/check": "Check and award eligible badges",
            "POST /user/{user_id}/mark-seen": "Mark badge notifications as seen",
            "GET /milestones": "Get all milestones",
            "GET /user/{user_id}/milestones": "Get user's achieved milestones",
            "GET /leaderboard/badges": "Badge leaderboard"
        },
        "badge_tiers": {
            "1": "Bronze [★]",
            "2": "Silver [★★]",
            "3": "Gold [★★★]",
            "4": "Platinum [◆]"
        },
        "categories": ["level", "achievement", "quiz"],
        "total_badges": 21
    }


@router.get("/all-badges")
async def get_all_badges(category: Optional[str] = None):
    """
    Get all available badges, optionally filtered by category.
    
    Categories: level, achievement, quiz
    """
    try:
        query = supabase.table('badges').select('*').order('tier', 'requirement_value')
        
        if category:
            query = query.eq('category', category)
        
        result = query.execute()
        
        return {
            "badges": result.data,
            "count": len(result.data),
            "tiers": {
                "bronze": len([b for b in result.data if b['tier'] == 1]),
                "silver": len([b for b in result.data if b['tier'] == 2]),
                "gold": len([b for b in result.data if b['tier'] == 3]),
                "platinum": len([b for b in result.data if b['tier'] == 4])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get badges: {str(e)}")


@router.get("/user/{user_id}/badges")
async def get_user_badges(user_id: str, unseen_only: bool = False):
    """
    Get badges unlocked by a specific user.
    
    Query params:
    - unseen_only: If true, only return badges user hasn't seen yet
    """
    try:
        query = supabase.table('user_badges').select('''
            id,
            badge_id,
            unlocked_at,
            seen,
            metadata,
            badges (
                badge_key,
                name,
                description,
                symbol,
                tier,
                category
            )
        ''').eq('user_id', user_id)
        
        if unseen_only:
            query = query.eq('seen', False)
        
        result = query.order('unlocked_at', desc=True).execute()
        
        # Format response
        formatted_badges = []
        for ub in result.data:
            badge = ub['badges']
            formatted_badges.append({
                "id": ub['id'],
                "badge_id": ub['badge_id'],
                "badge_key": badge['badge_key'],
                "name": badge['name'],
                "description": badge['description'],
                "symbol": badge['symbol'],
                "tier": badge['tier'],
                "category": badge['category'],
                "unlocked_at": ub['unlocked_at'],
                "seen": ub['seen'],
                "metadata": ub['metadata']
            })
        
        return {
            "user_id": user_id,
            "badges": formatted_badges,
            "count": len(formatted_badges),
            "unseen_count": len([b for b in formatted_badges if not b['seen']])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user badges: {str(e)}")


@router.get("/user/{user_id}/summary")
async def get_user_achievements_summary(user_id: str):
    """
    Get summary of user's achievements (badge counts, milestones).
    """
    try:
        # Use the view
        summary = supabase.table('user_achievements_summary').select('*').eq('user_id', user_id).single().execute()
        
        if not summary.data:
            return {
                "user_id": user_id,
                "total_badges": 0,
                "bronze_badges": 0,
                "silver_badges": 0,
                "gold_badges": 0,
                "platinum_badges": 0,
                "total_milestones": 0,
                "latest_badge_at": None
            }
        
        return summary.data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get achievements summary: {str(e)}")


@router.post("/user/{user_id}/check")
async def check_and_award_badges(user_id: str):
    """
    Check user's stats and award any eligible badges.
    Returns list of newly unlocked badges.
    """
    try:
        # Call the Postgres function
        result = supabase.rpc('check_and_award_badges', {'p_user_id': user_id}).execute()
        
        # Filter for newly unlocked badges
        newly_unlocked = [b for b in result.data if b.get('newly_unlocked', False)]
        
        return {
            "user_id": user_id,
            "newly_unlocked": newly_unlocked,
            "count": len(newly_unlocked)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check badges: {str(e)}")


@router.post("/user/{user_id}/mark-seen")
async def mark_badges_as_seen(user_id: str, badge_ids: List[str] = None):
    """
    Mark badge notifications as seen by the user.
    If badge_ids provided, mark only those. Otherwise mark all unseen.
    """
    try:
        query = supabase.table('user_badges').update({'seen': True}).eq('user_id', user_id)
        
        if badge_ids:
            query = query.in_('id', badge_ids)
        else:
            query = query.eq('seen', False)
        
        result = query.execute()
        
        return {
            "success": True,
            "message": f"Marked {len(result.data)} badges as seen"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark badges as seen: {str(e)}")


@router.get("/milestones")
async def get_all_milestones(category: Optional[str] = None):
    """
    Get all available milestones, optionally filtered by category.
    
    Categories: xp, quiz, topic
    """
    try:
        query = supabase.table('milestones').select('*').order('threshold')
        
        if category:
            query = query.eq('category', category)
        
        result = query.execute()
        
        return {
            "milestones": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get milestones: {str(e)}")


@router.get("/user/{user_id}/milestones")
async def get_user_milestones(user_id: str):
    """Get milestones achieved by a specific user"""
    try:
        result = supabase.table('user_milestones').select('''
            id,
            milestone_id,
            achieved_at,
            current_value,
            metadata,
            milestones (
                milestone_key,
                name,
                description,
                symbol,
                category,
                threshold
            )
        ''').eq('user_id', user_id).order('achieved_at', desc=True).execute()
        
        # Format response
        formatted_milestones = []
        for um in result.data:
            milestone = um['milestones']
            formatted_milestones.append({
                "id": um['id'],
                "milestone_id": um['milestone_id'],
                "milestone_key": milestone['milestone_key'],
                "name": milestone['name'],
                "description": milestone['description'],
                "symbol": milestone['symbol'],
                "category": milestone['category'],
                "threshold": milestone['threshold'],
                "achieved_at": um['achieved_at'],
                "current_value": um['current_value'],
                "metadata": um['metadata']
            })
        
        return {
            "user_id": user_id,
            "milestones": formatted_milestones,
            "count": len(formatted_milestones)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user milestones: {str(e)}")


@router.get("/leaderboard/badges")
async def get_badge_leaderboard(limit: int = 10):
    """
    Get leaderboard based on total badges earned.
    """
    try:
        result = supabase.table('user_achievements_summary').select('*').order('total_badges', desc=True).limit(limit).execute()
        
        return {
            "leaderboard": result.data,
            "count": len(result.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get badge leaderboard: {str(e)}")


@router.get("/user/{user_id}/progress")
async def get_badge_progress(user_id: str):
    """
    Get user's progress toward unearned badges.
    Shows current stats vs. requirements.
    """
    try:
        # Get user stats
        user = supabase.table('users').select('total_xp, level').eq('user_id', user_id).single().execute()
        
        # Get quiz count
        quiz_count = supabase.table('quiz_scores').select('id', count='exact').eq('user_id', user_id).execute()
        
        # Get topic stats
        topics_mastered = supabase.table('user_topics').select('topic', count='exact').eq('user_id', user_id).eq('status', 'mastered').execute()
        topics_completed = supabase.table('user_topics').select('topic', count='exact').eq('user_id', user_id).in_('status', ['completed', 'mastered']).execute()
        
        # Get unlocked badge IDs
        unlocked = supabase.table('user_badges').select('badge_id').eq('user_id', user_id).execute()
        unlocked_ids = [ub['badge_id'] for ub in unlocked.data]
        
        # Get all badges not yet unlocked
        all_badges = supabase.table('badges').select('*').order('tier', 'requirement_value').execute()
        
        current_stats = {
            'level': user.data['level'],
            'total_xp': user.data['total_xp'],
            'quizzes_completed': quiz_count.count,
            'topics_mastered': topics_mastered.count,
            'topics_completed': topics_completed.count
        }
        
        # Calculate progress for each unearned badge
        progress = []
        for badge in all_badges.data:
            if badge['id'] not in unlocked_ids:
                current_value = current_stats.get(badge['requirement_type'], 0)
                percentage = min(100, (current_value / badge['requirement_value']) * 100)
                
                progress.append({
                    "badge_key": badge['badge_key'],
                    "name": badge['name'],
                    "description": badge['description'],
                    "symbol": badge['symbol'],
                    "tier": badge['tier'],
                    "requirement_type": badge['requirement_type'],
                    "requirement_value": badge['requirement_value'],
                    "current_value": current_value,
                    "percentage": round(percentage, 1),
                    "remaining": badge['requirement_value'] - current_value
                })
        
        return {
            "user_id": user_id,
            "current_stats": current_stats,
            "badge_progress": progress,
            "count": len(progress)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get badge progress: {str(e)}")
