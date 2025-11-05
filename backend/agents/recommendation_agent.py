"""
Study Recommendation Agent - Suggests personalized learning paths
Analyzes user progress, identifies weak areas, and recommends next topics
"""

import httpx
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


class RecommendationAgent:
    """
    Generates personalized study recommendations based on user performance.
    
    Analyzes:
    - Topics with low scores (weak areas)
    - Topics not yet studied
    - Topics studied long ago (need review)
    - User's learning patterns and preferences
    """
    
    # Recommendation criteria weights
    WEAK_AREA_THRESHOLD = 70  # Scores below this are considered weak
    STALE_DAYS = 7  # Topics not studied in this many days need review
    MIN_ATTEMPTS_FOR_MASTERY = 3  # Number of attempts before considering mastered
    
    # XP estimation factors
    BASE_XP_ESTIMATE = 150  # Average XP per quiz
    DIFFICULTY_MULTIPLIERS = {
        'easy': 0.8,    # 80% of base
        'medium': 1.0,  # 100% of base
        'hard': 1.3,    # 130% of base
        'expert': 1.5   # 150% of base
    }
    
    # AI Models
    MODELS = {
        'primary': "google/gemini-2.0-flash-exp:free",
        'fallback': "meta-llama/llama-3.2-3b-instruct:free"
    }
    
    @staticmethod
    def analyze_weak_areas(user_progress: List[Dict]) -> List[Dict]:
        """
        Identify topics where user is struggling.
        
        Args:
            user_progress: List of user's quiz attempts with scores
            
        Returns:
            List of weak topics with details
        """
        topic_performance = {}
        
        for attempt in user_progress:
            if not isinstance(attempt, dict):
                continue
            
            topic = attempt.get('topic')
            score = attempt.get('avg_score')
            attempts = attempt.get('total_attempts', 0)
            last_attempt = attempt.get('last_attempt')
            
            # Skip if topic is missing or score is None/invalid
            if not topic or score is None:
                continue
            
            # Ensure score is numeric
            try:
                score = float(score)
            except (ValueError, TypeError):
                continue
            
            if topic not in topic_performance:
                topic_performance[topic] = {
                    'topic': topic,
                    'scores': [],
                    'total_attempts': 0,
                    'last_attempt': None
                }
            
            topic_performance[topic]['scores'].append(score)
            topic_performance[topic]['total_attempts'] = attempts
            topic_performance[topic]['last_attempt'] = last_attempt
        
        # Identify weak areas
        weak_areas = []
        for topic, data in topic_performance.items():
            if not data['scores']:
                continue
            
            avg_score = sum(data['scores']) / len(data['scores'])
            
            if avg_score < RecommendationAgent.WEAK_AREA_THRESHOLD:
                weak_areas.append({
                    'topic': topic,
                    'avg_score': round(avg_score, 1),
                    'total_attempts': data['total_attempts'],
                    'last_attempt': data['last_attempt'],
                    'gap': round(RecommendationAgent.WEAK_AREA_THRESHOLD - avg_score, 1),
                    'reason': 'weak_performance'
                })
        
        # Sort by gap (biggest gaps first)
        weak_areas.sort(key=lambda x: x['gap'], reverse=True)
        
        return weak_areas
    
    @staticmethod
    def analyze_stale_topics(user_progress: List[Dict]) -> List[Dict]:
        """
        Identify topics that haven't been studied recently.
        
        Args:
            user_progress: List of user's quiz attempts
            
        Returns:
            List of stale topics needing review
        """
        stale_topics = []
        current_time = datetime.now()
        stale_threshold = current_time - timedelta(days=RecommendationAgent.STALE_DAYS)
        
        for attempt in user_progress:
            topic = attempt.get('topic')
            last_attempt = attempt.get('last_attempt')
            avg_score = attempt.get('avg_score', 0)
            
            if not topic or not last_attempt:
                continue
            
            # Parse last_attempt (assumes ISO format)
            try:
                if isinstance(last_attempt, str):
                    last_attempt_date = datetime.fromisoformat(last_attempt.replace('Z', '+00:00'))
                else:
                    last_attempt_date = last_attempt
                
                days_since = (current_time - last_attempt_date).days
                
                if days_since >= RecommendationAgent.STALE_DAYS:
                    stale_topics.append({
                        'topic': topic,
                        'days_since_last_attempt': days_since,
                        'avg_score': round(avg_score, 1),
                        'reason': 'needs_review'
                    })
            except (ValueError, AttributeError):
                continue
        
        # Sort by days since last attempt (oldest first)
        stale_topics.sort(key=lambda x: x['days_since_last_attempt'], reverse=True)
        
        return stale_topics
    
    @staticmethod
    def identify_new_topics(
        user_progress: List[Dict],
        all_available_topics: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Identify topics user hasn't tried yet.
        
        Args:
            user_progress: List of user's quiz attempts
            all_available_topics: List of all possible topics
            
        Returns:
            List of new topics to explore
        """
        if not all_available_topics:
            # Default topic suggestions if none provided
            all_available_topics = [
                "Python Programming",
                "JavaScript Fundamentals",
                "Data Structures",
                "Algorithms",
                "Web Development",
                "Machine Learning",
                "Database Design",
                "System Design",
                "API Development",
                "Cloud Computing"
            ]
        
        # Get topics user has already attempted
        attempted_topics = {attempt.get('topic') for attempt in user_progress if attempt.get('topic')}
        
        # Find new topics
        new_topics = []
        for topic in all_available_topics:
            if topic not in attempted_topics:
                new_topics.append({
                    'topic': topic,
                    'reason': 'new_learning_opportunity',
                    'status': 'not_attempted'
                })
        
        return new_topics
    
    @staticmethod
    def estimate_xp_gain(
        topic: str,
        recommended_difficulty: str,
        current_avg_score: Optional[float] = None
    ) -> int:
        """
        Estimate potential XP gain for a topic.
        
        Args:
            topic: Topic name
            recommended_difficulty: Suggested difficulty level
            current_avg_score: User's current average score
            
        Returns:
            Estimated XP gain
        """
        base_xp = RecommendationAgent.BASE_XP_ESTIMATE
        difficulty_multiplier = RecommendationAgent.DIFFICULTY_MULTIPLIERS.get(
            recommended_difficulty, 1.0
        )
        
        estimated_xp = int(base_xp * difficulty_multiplier)
        
        # Bonus XP for weak areas (improvement potential)
        if current_avg_score and current_avg_score < RecommendationAgent.WEAK_AREA_THRESHOLD:
            improvement_bonus = int((RecommendationAgent.WEAK_AREA_THRESHOLD - current_avg_score) * 0.5)
            estimated_xp += improvement_bonus
        
        return estimated_xp
    
    @staticmethod
    def prioritize_recommendations(
        weak_areas: List[Dict],
        stale_topics: List[Dict],
        new_topics: List[Dict],
        max_recommendations: int = 5
    ) -> List[Dict]:
        """
        Prioritize and combine recommendations.
        
        Priority Order:
        1. Weak areas (immediate improvement needed)
        2. Stale topics (prevent knowledge decay)
        3. New topics (expand knowledge base)
        
        Args:
            weak_areas: Topics with low scores
            stale_topics: Topics needing review
            new_topics: Unexplored topics
            max_recommendations: Maximum number of recommendations
            
        Returns:
            Prioritized list of recommendations
        """
        recommendations = []
        
        # Priority 1: Weak areas (most important)
        for weak in weak_areas[:max_recommendations]:
            recommendations.append({
                'topic': weak['topic'],
                'reason': f"Improve performance (current: {weak['avg_score']}%, goal: 70%+)",
                'priority': 'high',
                'category': 'weak_area',
                'current_score': weak['avg_score'],
                'recommended_difficulty': 'easy' if weak['avg_score'] < 50 else 'medium',
                'estimated_xp_gain': RecommendationAgent.estimate_xp_gain(
                    weak['topic'],
                    'easy' if weak['avg_score'] < 50 else 'medium',
                    weak['avg_score']
                ),
                'urgency': 'Address gaps in understanding'
            })
        
        # Priority 2: Stale topics (prevent forgetting)
        remaining_slots = max_recommendations - len(recommendations)
        for stale in stale_topics[:remaining_slots]:
            recommendations.append({
                'topic': stale['topic'],
                'reason': f"Review needed (last attempt: {stale['days_since_last_attempt']} days ago)",
                'priority': 'medium',
                'category': 'review',
                'current_score': stale['avg_score'],
                'recommended_difficulty': 'medium',
                'estimated_xp_gain': RecommendationAgent.estimate_xp_gain(
                    stale['topic'],
                    'medium',
                    stale['avg_score']
                ),
                'urgency': 'Maintain knowledge retention'
            })
        
        # Priority 3: New topics (expand knowledge)
        remaining_slots = max_recommendations - len(recommendations)
        for new in new_topics[:remaining_slots]:
            recommendations.append({
                'topic': new['topic'],
                'reason': "Expand your knowledge base with new topic",
                'priority': 'low',
                'category': 'new_learning',
                'current_score': None,
                'recommended_difficulty': 'medium',
                'estimated_xp_gain': RecommendationAgent.estimate_xp_gain(
                    new['topic'],
                    'medium'
                ),
                'urgency': 'Broaden expertise'
            })
        
        return recommendations[:max_recommendations]
    
    @staticmethod
    async def generate_ai_recommendations(
        user_progress: List[Dict],
        recommendations: List[Dict],
        user_context: Optional[Dict] = None
    ) -> Dict:
        """
        Use AI to generate personalized recommendation explanations.
        
        Args:
            user_progress: User's performance history
            recommendations: Prioritized recommendations
            user_context: Additional user information
            
        Returns:
            Enhanced recommendations with AI-generated insights
        """
        if not OPENROUTER_API_KEY:
            # Return basic recommendations without AI enhancement
            return {
                'recommendations': recommendations,
                'ai_enhanced': False
            }
        
        # Build context for AI
        total_attempts = sum(p.get('total_attempts', 0) for p in user_progress)
        avg_overall_score = (
            sum(p.get('avg_score', 0) for p in user_progress) / len(user_progress)
            if user_progress else 0
        )
        
        prompt = f"""You are an expert learning advisor. Based on the student's performance data, provide personalized study recommendations.

Student Performance Summary:
- Total quiz attempts: {total_attempts}
- Overall average score: {avg_overall_score:.1f}%
- Topics studied: {len(user_progress)}

Top Recommendations:
{json.dumps(recommendations, indent=2)}

Provide:
1. A brief motivational message (2-3 sentences)
2. Key insight about their learning pattern
3. Specific advice for their top priority topic

Format as JSON:
{{
  "motivational_message": "...",
  "learning_insight": "...",
  "priority_advice": "..."
}}
"""
        
        try:
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "StudyQuest Recommendations"
            }
            
            payload = {
                "model": RecommendationAgent.MODELS['primary'],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educational advisor providing personalized learning recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500,
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    OPENROUTER_BASE_URL,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                ai_insights = json.loads(content)
                
                return {
                    'recommendations': recommendations,
                    'ai_enhanced': True,
                    'ai_insights': ai_insights,
                    'overall_stats': {
                        'total_attempts': total_attempts,
                        'avg_score': round(avg_overall_score, 1),
                        'topics_studied': len(user_progress)
                    }
                }
        
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            return {
                'recommendations': recommendations,
                'ai_enhanced': False,
                'overall_stats': {
                    'total_attempts': total_attempts,
                    'avg_score': round(avg_overall_score, 1),
                    'topics_studied': len(user_progress)
                }
            }
    
    @staticmethod
    async def get_study_recommendations(
        user_progress: List[Dict],
        all_available_topics: Optional[List[str]] = None,
        max_recommendations: int = 5,
        include_ai_insights: bool = True
    ) -> Dict:
        """
        Generate comprehensive study recommendations.
        
        Args:
            user_progress: User's quiz performance data
            all_available_topics: List of all possible topics
            max_recommendations: Maximum number of recommendations
            include_ai_insights: Whether to include AI-generated insights
            
        Returns:
            Dictionary with recommendations and insights
        """
        # Analyze different aspects
        weak_areas = RecommendationAgent.analyze_weak_areas(user_progress)
        stale_topics = RecommendationAgent.analyze_stale_topics(user_progress)
        new_topics = RecommendationAgent.identify_new_topics(user_progress, all_available_topics)
        
        # Prioritize and combine
        recommendations = RecommendationAgent.prioritize_recommendations(
            weak_areas, stale_topics, new_topics, max_recommendations
        )
        
        # Enhance with AI if requested
        if include_ai_insights and recommendations:
            return await RecommendationAgent.generate_ai_recommendations(
                user_progress, recommendations
            )
        else:
            return {
                'recommendations': recommendations,
                'ai_enhanced': False,
                'analysis': {
                    'weak_areas_count': len(weak_areas),
                    'stale_topics_count': len(stale_topics),
                    'new_topics_available': len(new_topics)
                }
            }
    
    @staticmethod
    def format_recommendation_response(recommendation_data: Dict) -> Dict:
        """
        Format recommendation data for API response.
        
        Args:
            recommendation_data: Raw recommendation data
            
        Returns:
            Formatted response
        """
        response = {
            'recommendations': recommendation_data.get('recommendations', []),
            'metadata': {
                'ai_enhanced': recommendation_data.get('ai_enhanced', False),
                'generated_at': datetime.now().isoformat()
            }
        }
        
        # Add AI insights if available
        if recommendation_data.get('ai_enhanced'):
            response['ai_insights'] = recommendation_data.get('ai_insights', {})
        
        # Add overall stats if available
        if 'overall_stats' in recommendation_data:
            response['overall_stats'] = recommendation_data['overall_stats']
        
        # Add analysis if available
        if 'analysis' in recommendation_data:
            response['analysis'] = recommendation_data['analysis']
        
        return response
