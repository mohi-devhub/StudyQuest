"""
Adaptive Quiz Utilities
Helper functions for fetching user performance data and determining adaptive difficulty
"""

from typing import Dict, Optional, List
from config.supabase_client import supabase


class AdaptiveQuizHelper:
    """Helper functions for adaptive quiz generation"""
    
    @staticmethod
    async def get_user_performance_data(user_id: str, topic: Optional[str] = None) -> Dict:
        """
        Fetch user's past quiz performance data from Supabase.
        
        Args:
            user_id: User's UUID
            topic: Optional specific topic to filter by
            
        Returns:
            Dictionary with performance metrics
        """
        try:
            # Get progress data
            query = supabase.table('progress').select('*').eq('user_id', user_id)
            
            if topic:
                query = query.eq('topic', topic)
            
            result = query.execute()
            
            if not result.data:
                # No previous quiz data
                return {
                    'has_history': False,
                    'avg_score': 0.0,
                    'total_attempts': 0,
                    'last_difficulty': 'medium',
                    'topics_attempted': [],
                    'recommendation': 'medium'
                }
            
            # Calculate aggregate performance
            progress_records = result.data
            
            # Calculate overall average
            total_score = sum(float(p['avg_score']) for p in progress_records)
            avg_score = total_score / len(progress_records) if progress_records else 0.0
            
            # Get total attempts across all topics
            total_attempts = sum(p['total_attempts'] for p in progress_records)
            
            # Get topics attempted
            topics_attempted = [p['topic'] for p in progress_records]
            
            # Get last difficulty from XP logs if available
            last_difficulty = await AdaptiveQuizHelper._get_last_difficulty(user_id, topic)
            
            return {
                'has_history': True,
                'avg_score': round(avg_score, 2),
                'total_attempts': total_attempts,
                'last_difficulty': last_difficulty,
                'topics_attempted': topics_attempted,
                'topics_completed': sum(1 for p in progress_records if p['completion_status'] == 'completed'),
                'topics_in_progress': sum(1 for p in progress_records if p['completion_status'] == 'in_progress'),
                'recommendation': last_difficulty  # Will be updated by adaptive agent
            }
            
        except Exception as e:
            # Return default if error
            print(f"Error fetching performance data: {str(e)}")
            return {
                'has_history': False,
                'avg_score': 0.0,
                'total_attempts': 0,
                'last_difficulty': 'medium',
                'topics_attempted': [],
                'recommendation': 'medium'
            }
    
    @staticmethod
    async def _get_last_difficulty(user_id: str, topic: Optional[str] = None) -> str:
        """
        Get the last difficulty level used by the user.
        
        Checks XP logs for most recent quiz completion with difficulty metadata.
        """
        try:
            query = supabase.table('xp_logs').select('metadata').eq('user_id', user_id).eq('reason', 'quiz_completed').order('timestamp', desc=True)
            
            if topic:
                # Filter by topic in metadata
                result = query.execute()
                
                for log in result.data:
                    metadata = log.get('metadata', {})
                    if metadata.get('topic') == topic and 'difficulty' in metadata:
                        return metadata['difficulty']
            else:
                # Just get the most recent
                result = query.limit(1).execute()
                
                if result.data:
                    metadata = result.data[0].get('metadata', {})
                    if 'difficulty' in metadata:
                        return metadata['difficulty']
            
            return 'medium'  # Default
            
        except Exception as e:
            print(f"Error fetching last difficulty: {str(e)}")
            return 'medium'
    
    @staticmethod
    async def get_topic_performance(user_id: str, topic: str) -> Dict:
        """
        Get performance data for a specific topic.
        
        Args:
            user_id: User's UUID
            topic: Topic name
            
        Returns:
            Topic-specific performance metrics
        """
        try:
            result = supabase.table('progress').select('*').eq('user_id', user_id).eq('topic', topic).single().execute()
            
            if result.data:
                progress = result.data
                return {
                    'has_history': True,
                    'avg_score': float(progress['avg_score']),
                    'total_attempts': progress['total_attempts'],
                    'completion_status': progress['completion_status'],
                    'last_attempt': progress['last_attempt']
                }
            else:
                return {
                    'has_history': False,
                    'avg_score': 0.0,
                    'total_attempts': 0,
                    'completion_status': 'not_started',
                    'last_attempt': None
                }
                
        except Exception as e:
            print(f"Error fetching topic performance: {str(e)}")
            return {
                'has_history': False,
                'avg_score': 0.0,
                'total_attempts': 0,
                'completion_status': 'not_started',
                'last_attempt': None
            }
    
    @staticmethod
    async def get_adaptive_quiz_params(
        user_id: str,
        topic: Optional[str] = None,
        user_preference: Optional[str] = None
    ) -> Dict:
        """
        Get recommended parameters for adaptive quiz generation.
        
        Combines user performance data with adaptive algorithm to recommend:
        - Difficulty level
        - Number of questions
        - Question types
        
        Args:
            user_id: User's UUID
            topic: Optional topic name
            user_preference: Optional user-specified difficulty preference
            
        Returns:
            Dictionary with recommended quiz parameters
        """
        # Get performance data
        if topic:
            perf_data = await AdaptiveQuizHelper.get_topic_performance(user_id, topic)
        else:
            perf_data = await AdaptiveQuizHelper.get_user_performance_data(user_id)
        
        # Import here to avoid circular imports
        from agents.adaptive_quiz_agent import AdaptiveQuizAgent
        
        # Determine next difficulty
        avg_score = perf_data.get('avg_score', 0.0)
        last_difficulty = perf_data.get('last_difficulty', 'medium')
        total_attempts = perf_data.get('total_attempts', 0)
        
        # Get difficulty recommendation
        next_difficulty = AdaptiveQuizAgent.determine_next_difficulty(
            current_difficulty=last_difficulty,
            avg_score=avg_score,
            user_preference=user_preference
        )
        
        # Get detailed recommendation with reasoning
        recommendation = AdaptiveQuizAgent.get_difficulty_recommendation(
            avg_score=avg_score,
            current_difficulty=last_difficulty,
            recommended_difficulty=next_difficulty,
            total_attempts=total_attempts
        )
        
        # Determine number of questions based on performance
        if avg_score >= 90:
            num_questions = 7  # More questions for high performers
        elif avg_score >= 70:
            num_questions = 5  # Standard
        else:
            num_questions = 4  # Fewer questions for struggling students
        
        return {
            'difficulty': next_difficulty,
            'num_questions': num_questions,
            'recommendation': recommendation,
            'user_performance': {
                'avg_score': avg_score,
                'total_attempts': total_attempts,
                'has_history': perf_data.get('has_history', False)
            },
            'user_preference': user_preference,
            'adaptive_mode': 'enabled'
        }
    
    @staticmethod
    def format_adaptive_response(
        quiz_data: Dict,
        adaptive_params: Dict
    ) -> Dict:
        """
        Format the adaptive quiz response with metadata.
        
        Args:
            quiz_data: Raw quiz data from agent
            adaptive_params: Adaptive parameters used
            
        Returns:
            Formatted response with adaptive metadata
        """
        return {
            'topic': quiz_data.get('topic', 'Unknown'),
            'difficulty': adaptive_params['difficulty'],
            'questions': quiz_data['questions'],
            'adaptive_info': {
                'difficulty_selected': adaptive_params['difficulty'],
                'difficulty_recommended': adaptive_params['recommendation']['recommended_difficulty'],
                'reasoning': adaptive_params['recommendation']['reasoning'],
                'user_avg_score': adaptive_params['user_performance']['avg_score'],
                'total_attempts': adaptive_params['user_performance']['total_attempts'],
                'adaptive_mode': True,
                'user_preference_applied': adaptive_params['user_preference'] is not None
            },
            'metadata': {
                'num_questions': len(quiz_data['questions']),
                'cognitive_level': quiz_data.get('metadata', {}).get('cognitive_level', 'unknown'),
                'generated_with': quiz_data.get('metadata', {}).get('model', 'unknown')
            }
        }
