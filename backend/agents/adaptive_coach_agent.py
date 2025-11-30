"""
Adaptive Coach Agent
Analyzes user performance and provides personalized feedback and recommendations
"""
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from config.supabase_client import supabase
from utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def sanitize_input(input_text: str) -> str:
    """Sanitize user input to prevent prompt injection"""
    dangerous_patterns = [
        "ignore previous instructions",
        "ignore all previous",
        "disregard previous",
        "forget previous",
        "new instructions:",
        "system:",
        "assistant:",
    ]
    
    lower_input = input_text.lower()
    for pattern in dangerous_patterns:
        if pattern in lower_input:
            raise ValueError(f"Invalid input detected: potential prompt injection")
    
    return input_text.strip()


def get_gemini_model(model: str = None):
    """Get Gemini model instance"""
    model_name = model or GEMINI_MODEL
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 500
        }
    )


def analyze_user_performance(user_id: str) -> Dict:
    """
    Analyze user's quiz performance from Supabase
    
    Returns:
        Dict with:
        - weak_topics: Topics with score < 60%
        - strong_topics: Topics with score >= 80%
        - recent_topics: Last 5 topics studied
        - overall_stats: Total quizzes, avg score, etc.
    """
    try:
        # Get user stats
        user_stats_response = supabase.table('users').select('*').eq('user_id', user_id).single().execute()
        user_stats = user_stats_response.data if user_stats_response.data else {}
        
        # Get topic performance from user_topics
        topics_response = supabase.table('user_topics').select('*').eq('user_id', user_id).execute()
        topics = topics_response.data if topics_response.data else []
        
        # Get recent quiz scores
        quiz_response = supabase.table('quiz_scores').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(10).execute()
        recent_quizzes = quiz_response.data if quiz_response.data else []
        
        # Categorize topics
        weak_topics = [t for t in topics if t.get('best_score', 0) < 60]
        strong_topics = [t for t in topics if t.get('best_score', 0) >= 80]
        recent_topics = [q.get('topic') for q in recent_quizzes[:5]]
        
        # Calculate overall stats (match frontend expectations)
        total_quizzes = len(recent_quizzes)
        avg_score = sum(q.get('score', 0) for q in recent_quizzes) / total_quizzes if total_quizzes > 0 else 0
        topics_studied = len(topics)  # Count unique topics from user_topics
        
        return {
            "user_stats": user_stats,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "recent_topics": list(set(recent_topics)),  # Unique topics
            "overall_stats": {
                "total_attempts": total_quizzes,  # Match frontend expectation
                "avg_score": avg_score,  # Match frontend expectation
                "topics_studied": topics_studied,  # Match frontend expectation
                "total_xp": user_stats.get('total_xp', 0),
                "level": user_stats.get('level', 1)
            }
        }
    except Exception as e:
        logger.error("Error analyzing user performance", user_id=user_id, error=str(e))
        return {
            "user_stats": {},
            "weak_topics": [],
            "strong_topics": [],
            "recent_topics": [],
            "overall_stats": {
                "total_attempts": 0,  # Match frontend expectation
                "avg_score": 0,  # Match frontend expectation
                "topics_studied": 0,  # Match frontend expectation
                "total_xp": 0,
                "level": 1
            }
        }


def generate_topic_recommendations(
    weak_topics: List[Dict],
    strong_topics: List[Dict],
    recent_topics: List[str]
) -> List[str]:
    """
    Generate new topic recommendations based on performance using Google Gemini
    
    Args:
        weak_topics: Topics user struggles with
        strong_topics: Topics user excels in
        recent_topics: Recently studied topics
        
    Returns:
        List of 3-5 recommended topics
    """
    try:
        model = get_gemini_model()
        
        # Build context
        weak_list = ", ".join([t.get('topic', '') for t in weak_topics[:5]])
        strong_list = ", ".join([t.get('topic', '') for t in strong_topics[:5]])
        recent_list = ", ".join(recent_topics[:5])
        
        prompt = f"""You are an educational advisor. Based on the user's learning history, 
suggest 3-5 new related topics they should study next. Consider:
1. Topics that complement their strong areas
2. Foundational topics for their weak areas
3. Progressive learning paths

Return ONLY a numbered list of topic names, one per line. No explanations.

User's learning profile:
Weak topics (< 60%): {weak_list or 'None yet'}
Strong topics (>= 80%): {strong_list or 'None yet'}
Recent topics: {recent_list or 'None yet'}

Suggest 3-5 new topics to study:"""

        response = model.generate_content(prompt)
        recommendations = response.text.strip().split('\n')
        
        # Clean up numbered list
        cleaned = []
        for rec in recommendations:
            # Remove numbering (1., 2., etc.)
            clean = rec.strip()
            if clean and len(clean) > 2:
                # Remove leading numbers and punctuation
                clean = clean.lstrip('0123456789.-) ')
                if clean:
                    cleaned.append(clean)
        
        return cleaned[:5]  # Max 5 recommendations
        
    except Exception as e:
        logger.error("Error generating topic recommendations", error=str(e), weak_topics_count=len(weak_topics))
        return ["Python Basics", "Data Structures", "Algorithms", "Web Development"]


def generate_motivational_message(
    avg_score: float,
    total_quizzes: int,
    level: int,
    weak_count: int,
    strong_count: int
) -> List[str]:
    """
    Generate 1-2 motivational messages based on performance
    
    Returns:
        List of 1-2 motivational messages
    """
    try:
        model = get_gemini_model()
        
        prompt = f"""You are a supportive coding mentor. Generate 1-2 short, motivational messages 
in a terminal/monospace style. Be encouraging but concise. Use ASCII art sparingly.
Keep messages under 100 characters each. Focus on progress and growth mindset.

User stats:
- Average score: {avg_score:.1f}%
- Total quizzes: {total_quizzes}
- Current level: {level}
- Weak topics: {weak_count}
- Strong topics: {strong_count}

Generate 1-2 motivational messages (one per line):"""

        response = model.generate_content(prompt)
        messages_list = [m.strip() for m in response.text.strip().split('\n') if m.strip()]
        
        return messages_list[:2]  # Max 2 messages
        
    except Exception as e:
        logger.error("Error generating motivational message", avg_score=avg_score, level=level, error=str(e))
        # Fallback messages
        if avg_score >= 80:
            return ["[✓] Outstanding work! Keep this momentum going!"]
        elif avg_score >= 60:
            return ["[▸] Good progress! Push through those challenging topics!"]
        else:
            return ["[!] Every expert was once a beginner. Keep learning!"]


async def generate_adaptive_feedback(user_id: str) -> Dict:
    """
    Main function to generate complete adaptive feedback
    
    Args:
        user_id: User ID to analyze
        
    Returns:
        Dict with:
        - weak_topics: List of topics to review
        - recommendations: New topics to study
        - motivational_messages: 1-2 encouraging messages
        - performance_summary: Overall stats
    """
    # Sanitize input
    user_id = sanitize_input(user_id)
    
    # Analyze performance
    analysis = analyze_user_performance(user_id)
    
    weak_topics = analysis['weak_topics']
    strong_topics = analysis['strong_topics']
    recent_topics = analysis['recent_topics']
    stats = analysis['overall_stats']
    
    # Generate recommendations
    recommendations = generate_topic_recommendations(
        weak_topics,
        strong_topics,
        recent_topics
    )
    
    # Generate motivational messages
    motivational_messages = generate_motivational_message(
        avg_score=stats['avg_score'],
        total_quizzes=stats['total_attempts'],
        level=stats['level'],
        weak_count=len(weak_topics),
        strong_count=len(strong_topics)
    )
    
    # Format weak topics for response
    weak_topics_formatted = [
        {
            "topic": t.get('topic'),
            "score": t.get('best_score'),
            "attempts": t.get('attempts'),
            "recommendation": "Review fundamentals and try again"
        }
        for t in weak_topics[:5]  # Top 5 weak topics
    ]
    
    return {
        "success": True,
        "user_id": user_id,
        "performance_summary": {
            "average_score": round(stats['avg_score'], 1),
            "total_quizzes": stats['total_attempts'],
            "level": stats['level'],
            "total_xp": stats['total_xp'],
            "weak_topics_count": len(weak_topics),
            "strong_topics_count": len(strong_topics)
        },
        "weak_topics": weak_topics_formatted,
        "recommended_topics": recommendations,
        "motivational_messages": motivational_messages,
        "next_steps": [
            f"Review {weak_topics_formatted[0]['topic']}" if weak_topics_formatted else "Keep practicing!",
            f"Try studying: {recommendations[0]}" if recommendations else "Explore new topics"
        ]
    }


# Sync version for use in routes
def generate_adaptive_feedback_sync(user_id: str) -> Dict:
    """Synchronous wrapper for adaptive feedback generation"""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(generate_adaptive_feedback(user_id))
