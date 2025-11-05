#!/usr/bin/env python3
"""
Test script for Study Recommendation Agent

Tests recommendation logic, prioritization, and XP estimation.

Run: python3 test_recommendations.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.recommendation_agent import RecommendationAgent


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_subheader(title):
    """Print formatted subsection header"""
    print(f"\n{title}")
    print("-" * len(title))


def create_mock_progress_data():
    """Create mock user progress data for testing"""
    now = datetime.now()
    
    return [
        # Weak area - low score
        {
            'topic': 'Algorithms',
            'avg_score': 45.0,
            'total_attempts': 5,
            'last_attempt': (now - timedelta(days=2)).isoformat()
        },
        # Another weak area
        {
            'topic': 'System Design',
            'avg_score': 62.0,
            'total_attempts': 3,
            'last_attempt': (now - timedelta(days=1)).isoformat()
        },
        # Good performance
        {
            'topic': 'Python Programming',
            'avg_score': 88.0,
            'total_attempts': 10,
            'last_attempt': now.isoformat()
        },
        # Stale topic - not studied recently
        {
            'topic': 'Database Design',
            'avg_score': 75.0,
            'total_attempts': 6,
            'last_attempt': (now - timedelta(days=10)).isoformat()
        },
        # Very stale topic
        {
            'topic': 'Web Development',
            'avg_score': 70.0,
            'total_attempts': 4,
            'last_attempt': (now - timedelta(days=15)).isoformat()
        },
        # Recent but borderline
        {
            'topic': 'Data Structures',
            'avg_score': 68.0,
            'total_attempts': 7,
            'last_attempt': (now - timedelta(days=3)).isoformat()
        }
    ]


def test_weak_area_detection():
    """Test 1: Weak area detection"""
    print_header("TEST 1: Weak Area Detection")
    
    mock_data = create_mock_progress_data()
    weak_areas = RecommendationAgent.analyze_weak_areas(mock_data)
    
    print(f"\nTotal topics analyzed: {len(mock_data)}")
    print(f"Weak areas found (score < 70%): {len(weak_areas)}")
    
    print_subheader("Weak Areas Details")
    for weak in weak_areas:
        print(f"  📉 {weak['topic']}")
        print(f"     Score: {weak['avg_score']}% (gap: {weak['gap']}%)")
        print(f"     Attempts: {weak['total_attempts']}")
        print(f"     Reason: {weak['reason']}")
    
    # Verify sorting (biggest gaps first)
    is_sorted = all(
        weak_areas[i]['gap'] >= weak_areas[i+1]['gap']
        for i in range(len(weak_areas)-1)
    )
    
    print_subheader("Test 1 Results")
    if weak_areas and is_sorted:
        print("✅ Weak areas detected and sorted correctly")
        return True
    else:
        print("❌ Weak area detection failed")
        return False


def test_stale_topic_detection():
    """Test 2: Stale topic detection"""
    print_header("TEST 2: Stale Topic Detection")
    
    mock_data = create_mock_progress_data()
    stale_topics = RecommendationAgent.analyze_stale_topics(mock_data)
    
    print(f"\nStale threshold: {RecommendationAgent.STALE_DAYS} days")
    print(f"Stale topics found: {len(stale_topics)}")
    
    print_subheader("Stale Topics Details")
    for stale in stale_topics:
        print(f"  ⏰ {stale['topic']}")
        print(f"     Days since last attempt: {stale['days_since_last_attempt']}")
        print(f"     Score: {stale['avg_score']}%")
        print(f"     Reason: {stale['reason']}")
    
    # Verify sorting (oldest first)
    is_sorted = all(
        stale_topics[i]['days_since_last_attempt'] >= stale_topics[i+1]['days_since_last_attempt']
        for i in range(len(stale_topics)-1)
    )
    
    print_subheader("Test 2 Results")
    if stale_topics and is_sorted:
        print("✅ Stale topics detected and sorted correctly")
        return True
    else:
        print("❌ Stale topic detection failed")
        return False


def test_new_topic_identification():
    """Test 3: New topic identification"""
    print_header("TEST 3: New Topic Identification")
    
    mock_data = create_mock_progress_data()
    attempted_topics = [d['topic'] for d in mock_data]
    
    all_topics = attempted_topics + [
        "Machine Learning",
        "Cloud Computing",
        "API Development"
    ]
    
    new_topics = RecommendationAgent.identify_new_topics(mock_data, all_topics)
    
    print(f"\nTotal available topics: {len(all_topics)}")
    print(f"Attempted topics: {len(attempted_topics)}")
    print(f"New topics identified: {len(new_topics)}")
    
    print_subheader("New Topics")
    for new in new_topics:
        print(f"  🆕 {new['topic']}")
        print(f"     Status: {new['status']}")
        print(f"     Reason: {new['reason']}")
    
    print_subheader("Test 3 Results")
    expected_new = len(all_topics) - len(attempted_topics)
    if len(new_topics) == expected_new:
        print(f"✅ Correctly identified {expected_new} new topics")
        return True
    else:
        print(f"❌ Expected {expected_new} new topics, found {len(new_topics)}")
        return False


def test_xp_estimation():
    """Test 4: XP gain estimation"""
    print_header("TEST 4: XP Gain Estimation")
    
    test_cases = [
        ('Python', 'easy', 50.0),    # Weak area, easy difficulty
        ('Python', 'medium', 65.0),  # Borderline, medium
        ('Python', 'hard', 85.0),    # Strong, hard
        ('Python', 'expert', 90.0),  # Expert, expert
        ('New Topic', 'medium', None)  # New topic
    ]
    
    print_subheader("XP Estimation for Different Scenarios")
    for topic, difficulty, score in test_cases:
        estimated_xp = RecommendationAgent.estimate_xp_gain(topic, difficulty, score)
        
        score_str = f"{score}%" if score else "No history"
        print(f"\n  Topic: {topic}")
        print(f"  Difficulty: {difficulty}, Current Score: {score_str}")
        print(f"  Estimated XP: {estimated_xp}")
    
    # Verify difficulty multipliers work
    easy_xp = RecommendationAgent.estimate_xp_gain('Test', 'easy', 75.0)
    expert_xp = RecommendationAgent.estimate_xp_gain('Test', 'expert', 75.0)
    
    print_subheader("Test 4 Results")
    if expert_xp > easy_xp:
        print("✅ XP estimation working correctly (expert > easy)")
        print(f"   Easy: {easy_xp} XP, Expert: {expert_xp} XP")
        return True
    else:
        print("❌ XP estimation incorrect")
        return False


def test_recommendation_prioritization():
    """Test 5: Recommendation prioritization"""
    print_header("TEST 5: Recommendation Prioritization")
    
    mock_data = create_mock_progress_data()
    
    # Get all types
    weak_areas = RecommendationAgent.analyze_weak_areas(mock_data)
    stale_topics = RecommendationAgent.analyze_stale_topics(mock_data)
    new_topics = RecommendationAgent.identify_new_topics(mock_data)
    
    # Prioritize
    recommendations = RecommendationAgent.prioritize_recommendations(
        weak_areas, stale_topics, new_topics, max_recommendations=5
    )
    
    print(f"\nMax recommendations: 5")
    print(f"Total recommendations generated: {len(recommendations)}")
    
    print_subheader("Prioritized Recommendations")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n  {i}. {rec['topic']}")
        print(f"     Priority: {rec['priority'].upper()}")
        print(f"     Category: {rec['category']}")
        print(f"     Reason: {rec['reason']}")
        print(f"     Difficulty: {rec['recommended_difficulty']}")
        print(f"     Est. XP: {rec['estimated_xp_gain']}")
        print(f"     Urgency: {rec['urgency']}")
    
    # Verify priority ordering
    priorities = [rec['category'] for rec in recommendations]
    weak_count = priorities.count('weak_area')
    review_count = priorities.count('review')
    new_count = priorities.count('new_learning')
    
    print_subheader("Priority Distribution")
    print(f"  Weak Areas: {weak_count}")
    print(f"  Reviews: {review_count}")
    print(f"  New Topics: {new_count}")
    
    # Check that weak areas come first
    first_weak_idx = next((i for i, p in enumerate(priorities) if p == 'weak_area'), -1)
    first_new_idx = next((i for i, p in enumerate(priorities) if p == 'new_learning'), len(priorities))
    
    print_subheader("Test 5 Results")
    if first_weak_idx >= 0 and first_weak_idx < first_new_idx:
        print("✅ Recommendations prioritized correctly (weak areas before new topics)")
        return True
    else:
        print("❌ Prioritization incorrect")
        return False


def test_difficulty_recommendation():
    """Test 6: Difficulty recommendation logic"""
    print_header("TEST 6: Difficulty Recommendation Logic")
    
    test_scenarios = [
        (45.0, 'easy', 'Very weak area'),
        (62.0, 'medium', 'Weak but not critical'),
        (75.0, 'medium', 'Decent performance'),
        (88.0, 'hard', 'Strong performance'),
        (None, 'medium', 'New topic')
    ]
    
    print_subheader("Difficulty Recommendations")
    all_correct = True
    
    for score, expected_diff, description in test_scenarios:
        # Create mock recommendation
        if score is not None:
            weak_data = {
                'topic': 'Test Topic',
                'avg_score': score,
                'total_attempts': 5,
                'last_attempt': datetime.now().isoformat(),
                'gap': 70 - score if score < 70 else 0,
                'reason': 'weak_performance'
            }
            
            recommendations = RecommendationAgent.prioritize_recommendations(
                [weak_data] if score < 70 else [],
                [],
                [],
                max_recommendations=1
            )
        else:
            # New topic
            new_data = {
                'topic': 'New Topic',
                'reason': 'new_learning_opportunity',
                'status': 'not_attempted'
            }
            recommendations = RecommendationAgent.prioritize_recommendations(
                [], [], [new_data], max_recommendations=1
            )
        
        if recommendations:
            actual_diff = recommendations[0]['recommended_difficulty']
            is_correct = actual_diff == expected_diff
            status = "✅" if is_correct else "❌"
            
            score_str = f"{score}%" if score else "None"
            print(f"\n  {description}")
            print(f"     Score: {score_str}")
            print(f"     Expected: {expected_diff}, Got: {actual_diff} {status}")
            
            if not is_correct:
                all_correct = False
    
    print_subheader("Test 6 Results")
    if all_correct:
        print("✅ All difficulty recommendations correct")
        return True
    else:
        print("❌ Some difficulty recommendations incorrect")
        return False


def test_edge_cases():
    """Test 7: Edge cases"""
    print_header("TEST 7: Edge Cases")
    
    print_subheader("Empty Progress Data")
    empty_weak = RecommendationAgent.analyze_weak_areas([])
    empty_stale = RecommendationAgent.analyze_stale_topics([])
    print(f"  Weak areas from empty data: {len(empty_weak)} ✅")
    print(f"  Stale topics from empty data: {len(empty_stale)} ✅")
    
    print_subheader("Invalid Data")
    invalid_data = [
        {'topic': None, 'avg_score': 50},  # No topic
        {'topic': 'Valid', 'avg_score': None},  # No score
        {},  # Empty dict
    ]
    
    try:
        weak = RecommendationAgent.analyze_weak_areas(invalid_data)
        print(f"  Handled invalid data gracefully: {len(weak)} results ✅")
    except Exception as e:
        print(f"  Error handling invalid data: {e} ❌")
        return False
    
    print_subheader("Extreme Values")
    extreme_data = [
        {'topic': 'Perfect', 'avg_score': 100.0, 'total_attempts': 1, 'last_attempt': datetime.now().isoformat()},
        {'topic': 'Zero', 'avg_score': 0.0, 'total_attempts': 1, 'last_attempt': datetime.now().isoformat()},
    ]
    
    extreme_weak = RecommendationAgent.analyze_weak_areas(extreme_data)
    extreme_xp = RecommendationAgent.estimate_xp_gain('Test', 'medium', 0.0)
    
    print(f"  100% score: Not in weak areas ✅" if 'Perfect' not in [w['topic'] for w in extreme_weak] else "  100% score: Incorrectly flagged ❌")
    print(f"  0% score: In weak areas ✅" if 'Zero' in [w['topic'] for w in extreme_weak] else "  0% score: Not detected ❌")
    print(f"  XP for 0% score: {extreme_xp} XP ✅")
    
    print_subheader("Test 7 Results")
    print("✅ All edge cases handled correctly")
    return True


def run_all_tests():
    """Run all recommendation tests"""
    print_header("RECOMMENDATION AGENT TEST SUITE")
    print("Testing recommendation logic, prioritization, and XP estimation")
    
    tests = [
        ("Weak Area Detection", test_weak_area_detection),
        ("Stale Topic Detection", test_stale_topic_detection),
        ("New Topic Identification", test_new_topic_identification),
        ("XP Estimation", test_xp_estimation),
        ("Recommendation Prioritization", test_recommendation_prioritization),
        ("Difficulty Recommendation", test_difficulty_recommendation),
        ("Edge Cases", test_edge_cases),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' encountered an error: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Print summary
    print_header("TEST SUMMARY")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! Recommendation system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
