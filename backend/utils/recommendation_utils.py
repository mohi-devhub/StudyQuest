"""
Recommendation Helper Utilities
Fetches and processes user data for study recommendations
"""

from typing import Dict, List, Optional
from config.supabase_client import supabase


class RecommendationHelper:
    """Helper class for fetching and processing recommendation data."""

    @staticmethod
    async def fetch_user_progress(user_id: str) -> List[Dict]:
        """
        Fetch user's complete progress history from Supabase.

        Args:
            user_id: User's unique identifier

        Returns:
            List of progress records with topic, score, attempts, etc.
        """
        try:
            # Fetch from user_topics table (updated by triggers when quizzes are submitted)
            response = supabase.table("user_topics").select(
                "topic, best_score, attempts, last_attempted_at, status, created_at, updated_at"
            ).eq("user_id", user_id).execute()

            if not response.data:
                return []

            # Transform to match expected format
            return [
                {
                    'topic': item['topic'],
                    'avg_score': item['best_score'],  # Use best_score as avg_score
                    'quizzes_completed': item['attempts'],
                    'last_completed_at': item['last_attempted_at'],
                    'status': item.get('status'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at')
                }
                for item in response.data
            ]

        except Exception as e:
            print(f"Error fetching user progress: {e}")
            return []

    @staticmethod
    async def fetch_weak_areas(user_id: str, threshold: float = 70.0) -> List[Dict]:
        """
        Fetch topics where user is performing below threshold.

        Args:
            user_id: User's unique identifier
            threshold: Score threshold for weak areas

        Returns:
            List of weak area topics
        """
        try:
            # Fetch topics with low scores from user_topics
            response = supabase.table("user_topics").select(
                "topic, best_score, attempts, last_attempted_at"
            ).eq("user_id", user_id).lt("best_score", threshold).order(
                "best_score", desc=False
            ).execute()

            if not response.data:
                return []

            # Transform to match expected format
            return [
                {
                    'topic': item['topic'],
                    'avg_score': item['best_score'],
                    'quizzes_completed': item['attempts'],
                    'last_completed_at': item['last_attempted_at']
                }
                for item in response.data
            ]

        except Exception as e:
            print(f"Error fetching weak areas: {e}")
            return []

    @staticmethod
    async def fetch_topic_details(user_id: str, topic: str) -> Optional[Dict]:
        """
        Fetch detailed progress for a specific topic.

        Args:
            user_id: User's unique identifier
            topic: Topic name

        Returns:
            Topic progress details or None
        """
        try:
            response = supabase.table("user_topics").select(
                "topic, best_score, attempts, last_attempted_at, status, created_at, updated_at"
            ).eq("user_id", user_id).eq("topic", topic).execute()

            if response.data:
                item = response.data[0]
                return {
                    'topic': item['topic'],
                    'avg_score': item['best_score'],
                    'quizzes_completed': item['attempts'],
                    'last_completed_at': item['last_attempted_at'],
                    'status': item.get('status'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at')
                }
            return None

        except Exception as e:
            print(f"Error fetching topic details: {e}")
            return None

    @staticmethod
    async def fetch_xp_history(user_id: str, limit: int = 50) -> List[Dict]:
        """
        Fetch user's XP history for pattern analysis.

        Args:
            user_id: User's unique identifier
            limit: Maximum number of records to fetch

        Returns:
            List of XP log entries
        """
        try:
            response = supabase.table("xp_logs").select(
                "source, xp_amount, metadata, created_at"
            ).eq("user_id", user_id).order(
                "created_at", desc=True
            ).limit(limit).execute()

            return response.data if response.data else []

        except Exception as e:
            print(f"Error fetching XP history: {e}")
            return []

    @staticmethod
    async def get_all_topics_from_progress(user_id: Optional[str] = None) -> List[str]:
        """
        Get list of all unique topics from progress table.

        Args:
            user_id: Optional user ID to filter by

        Returns:
            List of unique topic names
        """
        try:
            query = supabase.table("user_topics").select("topic")

            if user_id:
                query = query.eq("user_id", user_id)

            response = query.execute()

            if response.data:
                # Extract unique topics
                topics = list(set(record['topic'] for record in response.data if record.get('topic')))
                return sorted(topics)

            return []

        except Exception as e:
            print(f"Error fetching all topics: {e}")
            return []

    @staticmethod
    async def calculate_learning_velocity(user_id: str) -> Dict:
        """
        Calculate user's learning velocity (improvement rate).

        Args:
            user_id: User's unique identifier

        Returns:
            Dictionary with velocity metrics
        """
        try:
            xp_history = await RecommendationHelper.fetch_xp_history(user_id, limit=20)

            if len(xp_history) < 5:
                return {
                    'velocity': 'insufficient_data',
                    'trend': 'unknown',
                    'recent_xp_avg': 0
                }

            # Calculate recent XP average (last 5 activities)
            recent_xp = [log.get('xp_amount', 0) for log in xp_history[:5]]
            recent_avg = sum(recent_xp) / len(recent_xp) if recent_xp else 0

            # Calculate older XP average (previous 5 activities)
            older_xp = [log.get('xp_amount', 0) for log in xp_history[5:10]]
            older_avg = sum(older_xp) / len(older_xp) if older_xp else 0

            # Determine trend
            if recent_avg > older_avg * 1.1:
                trend = 'improving'
            elif recent_avg < older_avg * 0.9:
                trend = 'declining'
            else:
                trend = 'stable'

            # Calculate velocity (rate of change)
            if older_avg > 0:
                velocity = round(((recent_avg - older_avg) / older_avg) * 100, 1)
            else:
                velocity = 0

            return {
                'velocity': velocity,
                'trend': trend,
                'recent_xp_avg': round(recent_avg, 1),
                'older_xp_avg': round(older_avg, 1)
            }

        except Exception as e:
            print(f"Error calculating learning velocity: {e}")
            return {
                'velocity': 'error',
                'trend': 'unknown',
                'recent_xp_avg': 0
            }

    @staticmethod
    def format_user_context(
        user_progress: List[Dict],
        xp_history: List[Dict],
        learning_velocity: Dict
    ) -> Dict:
        """
        Format comprehensive user context for recommendations.

        Args:
            user_progress: User's topic progress
            xp_history: User's XP log history
            learning_velocity: Velocity metrics

        Returns:
            Formatted user context
        """
        # Calculate overall metrics
        total_attempts = sum(p.get('quizzes_completed', 0) for p in user_progress)
        avg_score = (
            sum(p.get('avg_score', 0) for p in user_progress) / len(user_progress)
            if user_progress else 0
        )
        total_xp = sum(log.get('xp_amount', 0) for log in xp_history)

        # Identify performance level
        if avg_score >= 85:
            performance_level = 'expert'
        elif avg_score >= 70:
            performance_level = 'proficient'
        elif avg_score >= 50:
            performance_level = 'developing'
        else:
            performance_level = 'beginner'

        return {
            'total_attempts': total_attempts,
            'avg_score': round(avg_score, 1),
            'total_xp': total_xp,
            'topics_studied': len(user_progress),
            'performance_level': performance_level,
            'learning_velocity': learning_velocity,
            'active_learner': total_attempts > 10
        }

    @staticmethod
    async def get_recommendation_data(user_id: str) -> Dict:
        """
        Fetch all data needed for generating recommendations.

        Args:
            user_id: User's unique identifier

        Returns:
            Complete recommendation data package
        """
        try:
            # Fetch all relevant data
            user_progress = await RecommendationHelper.fetch_user_progress(user_id)
            xp_history = await RecommendationHelper.fetch_xp_history(user_id)
            learning_velocity = await RecommendationHelper.calculate_learning_velocity(user_id)
            all_topics = await RecommendationHelper.get_all_topics_from_progress(user_id)

            # Format user context
            user_context = RecommendationHelper.format_user_context(
                user_progress, xp_history, learning_velocity
            )

            return {
                'user_progress': user_progress,
                'xp_history': xp_history,
                'learning_velocity': learning_velocity,
                'user_context': user_context,
                'all_available_topics': all_topics
            }

        except Exception as e:
            print(f"Error getting recommendation data: {e}")
            return {
                'user_progress': [],
                'xp_history': [],
                'learning_velocity': {'velocity': 'error', 'trend': 'unknown'},
                'user_context': {},
                'all_available_topics': []
            }
