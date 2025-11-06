"""
Progress tracking utilities for StudyQuest
Handles progress updates and XP point awards
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
from config.supabase_client import supabase


class ProgressTracker:
    """Manages user progress and XP tracking"""
    
    @staticmethod
    async def update_progress(
        user_id: str,
        topic: str,
        score: float,
        completion_status: str = "in_progress"
    ) -> Dict[str, Any]:
        """
        Update user progress for a topic after quiz completion
        
        Args:
            user_id: UUID of the user
            topic: Study topic name
            score: Quiz score as percentage (0-100)
            completion_status: 'not_started', 'in_progress', or 'completed'
            
        Returns:
            Updated progress record
        """
        try:
            # Call the Supabase function to update progress
            result = supabase.rpc(
                'update_progress_after_quiz',
                {
                    'p_user_id': user_id,
                    'p_topic': topic,
                    'p_score': score,
                    'p_completion_status': completion_status
                }
            ).execute()
            
            # Fetch the updated progress record
            progress = supabase.table('progress').select('*').eq('user_id', user_id).eq('topic', topic).single().execute()
            
            return progress.data
        except Exception as e:
            raise Exception(f"Failed to update progress: {str(e)}")
    
    @staticmethod
    async def get_user_progress(user_id: str, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get progress records for a user
        
        Args:
            user_id: UUID of the user
            topic: Optional topic filter
            
        Returns:
            List of progress records
        """
        try:
            query = supabase.table('progress').select('*').eq('user_id', user_id)
            
            if topic:
                query = query.eq('topic', topic)
            
            result = query.order('last_attempt', desc=True).execute()
            return result.data
        except Exception as e:
            raise Exception(f"Failed to fetch progress: {str(e)}")
    
    @staticmethod
    async def get_progress_stats(user_id: str) -> Dict[str, Any]:
        """
        Get aggregated progress statistics for a user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Statistics including total topics, completion rate, avg score
        """
        try:
            progress_records = await ProgressTracker.get_user_progress(user_id)
            
            if not progress_records:
                return {
                    'total_topics': 0,
                    'completed_topics': 0,
                    'in_progress_topics': 0,
                    'average_score': 0.0,
                    'completion_rate': 0.0
                }
            
            completed = sum(1 for p in progress_records if p['completion_status'] == 'completed')
            in_progress = sum(1 for p in progress_records if p['completion_status'] == 'in_progress')
            avg_score = sum(float(p['avg_score']) for p in progress_records) / len(progress_records)
            
            return {
                'total_topics': len(progress_records),
                'completed_topics': completed,
                'in_progress_topics': in_progress,
                'average_score': round(avg_score, 2),
                'completion_rate': round((completed / len(progress_records)) * 100, 2)
            }
        except Exception as e:
            raise Exception(f"Failed to calculate progress stats: {str(e)}")


class XPTracker:
    """Manages XP points and gamification"""
    
    # XP point values for different activities
    XP_VALUES = {
        'quiz_completed': 100,
        'perfect_score': 50,  # Bonus for 100% score
        'study_session': 50,
        'daily_streak': 25,
        'first_topic': 150,
        'topic_completed': 200
    }
    
    # Difficulty-based XP bonuses
    DIFFICULTY_BONUSES = {
        'easy': 10,
        'medium': 20,
        'hard': 30,
        'expert': 50
    }
    
    # Score tier bonuses (additional rewards for high performance)
    SCORE_TIER_BONUSES = {
        'perfect': 50,      # 100% score
        'excellent': 30,    # 90-99%
        'good': 15,         # 80-89%
        'passing': 0        # 70-79%
    }
    
    @staticmethod
    def calculate_xp(score: int, difficulty: str = 'medium') -> int:
        """
        Calculate XP points based on quiz score and difficulty level.
        
        This is the core XP calculation logic that determines rewards based on:
        1. Base score (proportional to percentage)
        2. Difficulty bonus (easy=10, medium=20, hard=30, expert=50)
        3. Performance tier bonus (perfect=50, excellent=30, good=15, passing=0)
        
        Args:
            score: Quiz score as integer percentage (0-100)
            difficulty: Difficulty level ('easy', 'medium', 'hard', 'expert')
            
        Returns:
            Total XP points to award
            
        Examples:
            >>> XPTracker.calculate_xp(100, 'hard')
            180  # 100 base + 30 difficulty + 50 perfect score
            
            >>> XPTracker.calculate_xp(85, 'medium')
            135  # 100 base + 20 difficulty + 15 good score
            
            >>> XPTracker.calculate_xp(75, 'easy')
            110  # 100 base + 10 difficulty + 0 passing
        """
        # Validate inputs
        score = max(0, min(100, score))  # Clamp score to 0-100
        difficulty = difficulty.lower()
        
        if difficulty not in XPTracker.DIFFICULTY_BONUSES:
            difficulty = 'medium'  # Default to medium if invalid
        
        # Base XP (always 100 for quiz completion)
        base_xp = XPTracker.XP_VALUES['quiz_completed']
        
        # Difficulty bonus
        difficulty_bonus = XPTracker.DIFFICULTY_BONUSES[difficulty]
        
        # Performance tier bonus based on score
        if score >= 100:
            performance_bonus = XPTracker.SCORE_TIER_BONUSES['perfect']
        elif score >= 90:
            performance_bonus = XPTracker.SCORE_TIER_BONUSES['excellent']
        elif score >= 80:
            performance_bonus = XPTracker.SCORE_TIER_BONUSES['good']
        else:
            performance_bonus = XPTracker.SCORE_TIER_BONUSES['passing']
        
        # Calculate total XP
        total_xp = base_xp + difficulty_bonus + performance_bonus
        
        return total_xp
    
    @staticmethod
    def get_difficulty_bonus(difficulty: str) -> int:
        """
        Get the XP bonus for a specific difficulty level.
        
        Args:
            difficulty: Difficulty level ('easy', 'medium', 'hard', 'expert')
            
        Returns:
            XP bonus points for the difficulty level
        """
        return XPTracker.DIFFICULTY_BONUSES.get(difficulty.lower(), 20)
    
    @staticmethod
    def get_score_tier(score: float) -> str:
        """
        Determine the performance tier based on score.
        
        Args:
            score: Quiz score as percentage (0-100)
            
        Returns:
            Tier name: 'perfect', 'excellent', 'good', or 'passing'
        """
        if score >= 100:
            return 'perfect'
        elif score >= 90:
            return 'excellent'
        elif score >= 80:
            return 'good'
        else:
            return 'passing'
    
    @staticmethod
    async def award_xp(
        user_id: str,
        reason: str,
        points: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Award XP points to a user
        
        Args:
            user_id: UUID of the user
            reason: Reason for XP award (e.g., 'quiz_completed')
            points: Optional custom point value (uses default if not provided)
            metadata: Optional additional data (quiz score, topic, etc.)
            
        Returns:
            Created XP log record
        """
        try:
            # Use default points if not provided
            if points is None:
                points = XPTracker.XP_VALUES.get(reason, 0)
            
            if metadata is None:
                metadata = {}
            
            # Call the Supabase function to award XP
            result = supabase.rpc(
                'award_xp',
                {
                    'p_user_id': user_id,
                    'p_points': points,
                    'p_reason': reason,
                    'p_metadata': metadata
                }
            ).execute()
            
            # Fetch the created XP log
            log_id = result.data
            xp_log = supabase.table('xp_logs').select('*').eq('id', log_id).single().execute()
            
            return xp_log.data
        except Exception as e:
            raise Exception(f"Failed to award XP: {str(e)}")
    
    @staticmethod
    async def get_user_xp_logs(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get XP logs for a user
        
        Args:
            user_id: UUID of the user
            limit: Maximum number of logs to return
            
        Returns:
            List of XP log records
        """
        try:
            result = supabase.table('xp_logs').select('*').eq('user_id', user_id).order('timestamp', desc=True).limit(limit).execute()
            return result.data
        except Exception as e:
            raise Exception(f"Failed to fetch XP logs: {str(e)}")
    
    @staticmethod
    async def get_total_xp(user_id: str) -> Dict[str, Any]:
        """
        Get total XP for a user
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Total XP and activity stats
        """
        try:
            result = supabase.table('user_total_xp').select('*').eq('user_id', user_id).single().execute()
            
            if result.data:
                return {
                    'user_id': result.data['user_id'],
                    'total_xp': result.data['total_xp'] or 0,
                    'total_activities': result.data['total_activities'] or 0,
                    'last_activity': result.data['last_activity']
                }
            else:
                return {
                    'user_id': user_id,
                    'total_xp': 0,
                    'total_activities': 0,
                    'last_activity': None
                }
        except Exception as e:
            # If no records exist yet, return zeros
            return {
                'user_id': user_id,
                'total_xp': 0,
                'total_activities': 0,
                'last_activity': None
            }
    
    @staticmethod
    async def calculate_quiz_xp(
        score: float,
        difficulty: str = 'medium',
        is_first_topic: bool = False
    ) -> int:
        """
        Calculate XP points for a quiz completion with all bonuses.
        
        This function uses the core calculate_xp() logic and adds special bonuses:
        - First topic bonus (if applicable)
        - Topic completion bonus (if score >= 70%)
        
        Args:
            score: Quiz score as percentage (0-100)
            difficulty: Difficulty level ('easy', 'medium', 'hard', 'expert')
            is_first_topic: Whether this is the user's first topic
            
        Returns:
            Total XP points to award including all bonuses
            
        Examples:
            >>> await XPTracker.calculate_quiz_xp(100, 'hard', True)
            330  # 180 base + 150 first topic
            
            >>> await XPTracker.calculate_quiz_xp(85, 'medium', False)
            135  # 135 base, no bonuses
        """
        # Use the core calculation logic
        xp = XPTracker.calculate_xp(int(score), difficulty)
        
        # Bonus for first topic
        if is_first_topic:
            xp += XPTracker.XP_VALUES['first_topic']
        
        # Bonus for completing topic (70%+ score)
        if score >= 70.0:
            # Only award topic completion bonus once (not on every attempt)
            # This will be checked in process_quiz_completion
            pass
        
        return xp
    
    @staticmethod
    async def process_quiz_completion(
        user_id: str,
        topic: str,
        score: float,
        total_questions: int,
        correct_answers: int,
        difficulty: str = 'medium'
    ) -> Dict[str, Any]:
        """
        Process quiz completion: update progress and award XP.
        
        This is the main function called after a quiz is completed. It:
        1. Checks if this is the user's first topic (for bonus)
        2. Updates progress in the database
        3. Calculates XP based on score, difficulty, and bonuses
        4. Awards XP and logs the activity
        
        Args:
            user_id: UUID of the user
            topic: Study topic
            score: Quiz score as percentage (0-100)
            total_questions: Total number of questions
            correct_answers: Number of correct answers
            difficulty: Quiz difficulty level ('easy', 'medium', 'hard', 'expert')
            
        Returns:
            Combined result with progress and XP data
            
        Example:
            >>> result = await XPTracker.process_quiz_completion(
            ...     user_id="uuid",
            ...     topic="Neural Networks",
            ...     score=95.0,
            ...     total_questions=5,
            ...     correct_answers=4,
            ...     difficulty="hard"
            ... )
            >>> print(result['xp_awarded']['points'])  # 160 (100 base + 30 hard + 30 excellent)
        """
        try:
            # Check if this is the first topic
            progress_records = await ProgressTracker.get_user_progress(user_id)
            is_first_topic = len(progress_records) == 0
            
            # Determine completion status
            completion_status = 'completed' if score >= 70.0 else 'in_progress'
            
            # Update progress
            progress = await ProgressTracker.update_progress(
                user_id=user_id,
                topic=topic,
                score=score,
                completion_status=completion_status
            )
            
            # Calculate XP with difficulty and bonuses
            xp_points = await XPTracker.calculate_quiz_xp(
                score=score,
                difficulty=difficulty,
                is_first_topic=is_first_topic
            )
            
            # Get performance tier for metadata
            score_tier = XPTracker.get_score_tier(score)
            difficulty_bonus = XPTracker.get_difficulty_bonus(difficulty)
            
            xp_log = await XPTracker.award_xp(
                user_id=user_id,
                reason='quiz_completed',
                points=xp_points,
                metadata={
                    'topic': topic,
                    'score': score,
                    'difficulty': difficulty,
                    'difficulty_bonus': difficulty_bonus,
                    'score_tier': score_tier,
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'completion_status': completion_status,
                    'is_first_topic': is_first_topic
                }
            )
            
            # Get updated total XP
            total_xp = await XPTracker.get_total_xp(user_id)
            
            return {
                'progress': progress,
                'xp_awarded': xp_log,
                'total_xp': total_xp['total_xp'],
                'completion_status': completion_status,
                'difficulty': difficulty,
                'score_tier': score_tier
            }
        except Exception as e:
            raise Exception(f"Failed to process quiz completion: {str(e)}")
