"""
Test Coach Agent feedback generation.

Run with: pytest backend/tests/test_coach_agent.py -v
"""

import pytest
from agents.coach_agent import CoachAgent, CoachFeedback


@pytest.fixture
def coach():
    """Initialize Coach Agent"""
    return CoachAgent()


def test_generate_feedback_high_score(coach):
    """Test feedback generation for high score (85%)"""
    feedback = coach.generate_feedback(
        topic="Python Programming",
        difficulty="medium",
        score=85,
        correct_answers=17,
        total_questions=20,
        xp_gained=165,
        next_difficulty="hard"
    )
    
    assert isinstance(feedback, CoachFeedback)
    assert len(feedback.motivational_message) > 0
    assert len(feedback.learning_insight) > 0
    assert len(feedback.improvement_tip) > 0
    assert len(feedback.next_steps) > 0
    
    # High score should be encouraging
    assert any(word in feedback.motivational_message.lower() for word in 
               ['great', 'excellent', 'outstanding', 'good', 'well done'])


def test_generate_feedback_medium_score(coach):
    """Test feedback generation for medium score (70%)"""
    feedback = coach.generate_feedback(
        topic="Data Structures",
        difficulty="medium",
        score=72,
        correct_answers=14.4,
        total_questions=20,
        xp_gained=145,
        next_difficulty="medium"
    )
    
    assert isinstance(feedback, CoachFeedback)
    # Should still be encouraging but suggest areas for improvement
    assert len(feedback.improvement_tip) > 0


def test_generate_feedback_low_score(coach):
    """Test feedback generation for low score (55%)"""
    feedback = coach.generate_feedback(
        topic="Algorithms",
        difficulty="hard",
        score=55,
        correct_answers=11,
        total_questions=20,
        xp_gained=120,
        next_difficulty="medium"
    )
    
    assert isinstance(feedback, CoachFeedback)
    # Should be supportive and constructive
    assert len(feedback.motivational_message) > 0
    assert len(feedback.next_steps) > 0


def test_generate_feedback_perfect_score(coach):
    """Test feedback generation for perfect score (100%)"""
    feedback = coach.generate_feedback(
        topic="Web Development",
        difficulty="easy",
        score=100,
        correct_answers=10,
        total_questions=10,
        xp_gained=180,
        next_difficulty="medium"
    )
    
    assert isinstance(feedback, CoachFeedback)
    # Should celebrate the achievement
    assert any(word in feedback.motivational_message.lower() for word in 
               ['perfect', 'excellent', 'outstanding', 'amazing'])


def test_fallback_feedback_high_score(coach):
    """Test fallback feedback for high scores"""
    feedback = coach._get_fallback_feedback(85, "Python", 165)
    
    assert isinstance(feedback, CoachFeedback)
    assert "Python" in feedback.motivational_message
    assert "165" in feedback.next_steps


def test_fallback_feedback_medium_score(coach):
    """Test fallback feedback for medium scores"""
    feedback = coach._get_fallback_feedback(72, "Data Structures", 145)
    
    assert isinstance(feedback, CoachFeedback)
    assert len(feedback.improvement_tip) > 0


def test_fallback_feedback_low_score(coach):
    """Test fallback feedback for low scores"""
    feedback = coach._get_fallback_feedback(55, "Algorithms", 120)
    
    assert isinstance(feedback, CoachFeedback)
    # Should be encouraging despite low score
    assert "give up" in feedback.motivational_message.lower()
    assert len(feedback.next_steps) > 0


def test_performance_level_classification(coach):
    """Test performance level calculation"""
    assert coach._get_performance_level(95) == "Exceptional"
    assert coach._get_performance_level(85) == "Excellent"
    assert coach._get_performance_level(75) == "Good"
    assert coach._get_performance_level(65) == "Satisfactory"
    assert coach._get_performance_level(55) == "Needs Improvement"


def test_batch_feedback_generation(coach):
    """Test generating feedback for multiple quiz results"""
    quiz_results = [
        {
            "topic": "Python",
            "difficulty": "medium",
            "score": 85,
            "correct_answers": 17,
            "total_questions": 20,
            "xp_gained": 165,
            "next_difficulty": "hard"
        },
        {
            "topic": "JavaScript",
            "difficulty": "easy",
            "score": 90,
            "correct_answers": 18,
            "total_questions": 20,
            "xp_gained": 155,
            "next_difficulty": "medium"
        }
    ]
    
    feedback_list = coach.generate_batch_feedback(quiz_results)
    
    assert len(feedback_list) == 2
    assert all(isinstance(f, CoachFeedback) for f in feedback_list)


def test_feedback_with_context(coach):
    """Test feedback generation with student context"""
    context = "Student has been consistently improving, averaging 75% over last 5 quizzes"
    
    feedback = coach.generate_feedback(
        topic="Python Programming",
        difficulty="medium",
        score=82,
        correct_answers=16,
        total_questions=20,
        xp_gained=160,
        next_difficulty="hard",
        context=context
    )
    
    assert isinstance(feedback, CoachFeedback)
    # Feedback should acknowledge improvement trend if AI picks up on context


def test_feedback_format_validation(coach):
    """Test that feedback follows expected format"""
    feedback = coach.generate_feedback(
        topic="Test Topic",
        difficulty="medium",
        score=80,
        correct_answers=16,
        total_questions=20,
        xp_gained=150,
        next_difficulty="hard"
    )
    
    # All fields should be strings
    assert isinstance(feedback.motivational_message, str)
    assert isinstance(feedback.learning_insight, str)
    assert isinstance(feedback.improvement_tip, str)
    assert isinstance(feedback.next_steps, str)
    
    # None should be empty
    assert feedback.motivational_message.strip() != ""
    assert feedback.learning_insight.strip() != ""
    assert feedback.improvement_tip.strip() != ""
    assert feedback.next_steps.strip() != ""
    
    # Should be reasonably concise (not too long)
    assert len(feedback.motivational_message) < 300
    assert len(feedback.learning_insight) < 300
    assert len(feedback.improvement_tip) < 200
    assert len(feedback.next_steps) < 200


if __name__ == "__main__":
    # Quick manual test
    coach = CoachAgent()
    feedback = coach.generate_feedback(
        topic="Python Programming",
        difficulty="medium",
        score=85,
        correct_answers=17,
        total_questions=20,
        xp_gained=165,
        next_difficulty="hard"
    )
    
    print("\nCoach Feedback Test:")
    print(f"Motivation: {feedback.motivational_message}")
    print(f"Insight: {feedback.learning_insight}")
    print(f"Tip: {feedback.improvement_tip}")
    print(f"Next Steps: {feedback.next_steps}")
