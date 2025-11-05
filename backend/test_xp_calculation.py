#!/usr/bin/env python3
"""
Test script for XP calculation logic
Demonstrates the calculate_xp() function with various scenarios
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.progress_tracker import XPTracker


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def test_calculate_xp():
    """Test the core calculate_xp function"""
    
    print_header("XP CALCULATION LOGIC TEST")
    print("\nBase XP: 100 points (quiz completion)")
    print("\nDifficulty Bonuses:")
    for difficulty, bonus in XPTracker.DIFFICULTY_BONUSES.items():
        print(f"  - {difficulty.capitalize():8s}: +{bonus} XP")
    
    print("\nScore Tier Bonuses:")
    for tier, bonus in XPTracker.SCORE_TIER_BONUSES.items():
        print(f"  - {tier.capitalize():10s}: +{bonus} XP")
    
    print_header("TEST SCENARIOS")
    
    # Test cases: (score, difficulty, expected_xp, description)
    test_cases = [
        # Perfect scores
        (100, 'easy', 160, "Perfect score on easy"),
        (100, 'medium', 170, "Perfect score on medium"),
        (100, 'hard', 180, "Perfect score on hard"),
        (100, 'expert', 200, "Perfect score on expert"),
        
        # Excellent scores (90-99%)
        (95, 'easy', 140, "Excellent score on easy"),
        (95, 'medium', 150, "Excellent score on medium"),
        (95, 'hard', 160, "Excellent score on hard"),
        (90, 'expert', 180, "Excellent score on expert"),
        
        # Good scores (80-89%)
        (85, 'easy', 125, "Good score on easy"),
        (85, 'medium', 135, "Good score on medium"),
        (85, 'hard', 145, "Good score on hard"),
        (80, 'expert', 165, "Good score on expert"),
        
        # Passing scores (70-79%)
        (75, 'easy', 110, "Passing score on easy"),
        (75, 'medium', 120, "Passing score on medium"),
        (75, 'hard', 130, "Passing score on hard"),
        (70, 'expert', 150, "Passing score on expert"),
        
        # Edge cases
        (100, 'invalid', 170, "Perfect with invalid difficulty (defaults to medium)"),
        (0, 'hard', 130, "Zero score on hard (still gets base + difficulty)"),
        (50, 'easy', 110, "Below passing on easy"),
    ]
    
    print("\n{:<5} {:<10} {:<12} {:<10} {:<40}".format(
        "Score", "Difficulty", "Total XP", "Expected", "Description"
    ))
    print("-" * 80)
    
    passed = 0
    failed = 0
    
    for score, difficulty, expected, description in test_cases:
        result = XPTracker.calculate_xp(score, difficulty)
        status = "✅" if result == expected else "❌"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} {score:>3}% {difficulty:<10} {result:>4} XP    {expected:>4} XP    {description}")
    
    print("\n" + "-" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print("❌ Some tests failed!")
        return False
    else:
        print("✅ All tests passed!")
        return True


def test_helper_functions():
    """Test helper functions"""
    
    print_header("HELPER FUNCTIONS TEST")
    
    print("\n1. get_difficulty_bonus()")
    print("-" * 40)
    for difficulty in ['easy', 'medium', 'hard', 'expert', 'invalid']:
        bonus = XPTracker.get_difficulty_bonus(difficulty)
        print(f"   {difficulty:<10}: {bonus} XP")
    
    print("\n2. get_score_tier()")
    print("-" * 40)
    test_scores = [100, 95, 90, 85, 80, 75, 70, 50, 0]
    for score in test_scores:
        tier = XPTracker.get_score_tier(float(score))
        print(f"   {score:>3}%: {tier}")
    
    print()


def demonstrate_real_world_scenarios():
    """Show real-world usage examples"""
    
    print_header("REAL-WORLD SCENARIOS")
    
    scenarios = [
        {
            "title": "Beginner Student - Easy Quiz",
            "score": 80,
            "difficulty": "easy",
            "context": "Student learning basics, gets good score"
        },
        {
            "title": "Average Student - Medium Quiz",
            "score": 85,
            "difficulty": "medium",
            "context": "Standard quiz, solid performance"
        },
        {
            "title": "Advanced Student - Hard Quiz",
            "score": 95,
            "difficulty": "hard",
            "context": "Challenging topic, excellent performance"
        },
        {
            "title": "Expert Challenge - Perfect Score",
            "score": 100,
            "difficulty": "expert",
            "context": "Maximum difficulty, perfect execution"
        },
        {
            "title": "Struggling Student - Barely Passing",
            "score": 70,
            "difficulty": "medium",
            "context": "Needs more practice, minimal XP"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print(f"   Context: {scenario['context']}")
        
        xp = XPTracker.calculate_xp(scenario['score'], scenario['difficulty'])
        tier = XPTracker.get_score_tier(float(scenario['score']))
        difficulty_bonus = XPTracker.get_difficulty_bonus(scenario['difficulty'])
        
        print(f"   Score: {scenario['score']}% | Difficulty: {scenario['difficulty']}")
        print(f"   → Total XP: {xp}")
        print(f"   → Breakdown: 100 base + {difficulty_bonus} difficulty + {XPTracker.SCORE_TIER_BONUSES[tier]} {tier}")


def compare_difficulties():
    """Compare XP across difficulties for same score"""
    
    print_header("DIFFICULTY COMPARISON (Same Score)")
    
    test_scores = [100, 90, 80, 70]
    
    print("\n{:<8} {:<8} {:<8} {:<8} {:<8}".format(
        "Score", "Easy", "Medium", "Hard", "Expert"
    ))
    print("-" * 50)
    
    for score in test_scores:
        easy_xp = XPTracker.calculate_xp(score, 'easy')
        medium_xp = XPTracker.calculate_xp(score, 'medium')
        hard_xp = XPTracker.calculate_xp(score, 'hard')
        expert_xp = XPTracker.calculate_xp(score, 'expert')
        
        print(f"{score:>3}%     {easy_xp:<8} {medium_xp:<8} {hard_xp:<8} {expert_xp:<8}")
    
    print("\nKey Insight: Higher difficulty = More XP for same performance")


def xp_ranges():
    """Show min/max XP ranges"""
    
    print_header("XP RANGES")
    
    print("\nMinimum XP (0% score):")
    for difficulty in ['easy', 'medium', 'hard', 'expert']:
        xp = XPTracker.calculate_xp(0, difficulty)
        print(f"  {difficulty.capitalize():8s}: {xp} XP")
    
    print("\nMaximum XP (100% score):")
    for difficulty in ['easy', 'medium', 'hard', 'expert']:
        xp = XPTracker.calculate_xp(100, difficulty)
        print(f"  {difficulty.capitalize():8s}: {xp} XP")
    
    print("\nRange per difficulty:")
    for difficulty in ['easy', 'medium', 'hard', 'expert']:
        min_xp = XPTracker.calculate_xp(0, difficulty)
        max_xp = XPTracker.calculate_xp(100, difficulty)
        print(f"  {difficulty.capitalize():8s}: {min_xp} - {max_xp} XP (range: {max_xp - min_xp})")


def main():
    """Run all tests"""
    
    print("\n" + "🎮" * 40)
    print("  StudyQuest XP Calculation System")
    print("🎮" * 40)
    
    # Run tests
    test_calculate_xp()
    test_helper_functions()
    demonstrate_real_world_scenarios()
    compare_difficulties()
    xp_ranges()
    
    print_header("SUMMARY")
    print("""
The XP calculation logic rewards:
✅ Higher quiz scores (perfect > excellent > good > passing)
✅ Higher difficulty levels (expert > hard > medium > easy)
✅ Perfect scores get the maximum bonus (+50 XP)
✅ All completed quizzes get base XP (100 points)

Example API Usage:
  POST /progress/calculate-xp
  {
    "score": 85,
    "difficulty": "hard"
  }
  
  Response: 145 XP (100 base + 30 hard + 15 good)

This encourages students to:
- Challenge themselves with harder material
- Strive for higher scores
- Learn from mistakes and improve
""")
    
    print("=" * 80)
    print("✅ XP Calculation Logic Test Complete!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
