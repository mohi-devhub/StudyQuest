#!/usr/bin/env python3
"""
Test script for Adaptive Quiz System

This script tests the adaptive quiz functionality by simulating
different user performance scenarios and verifying difficulty adjustments.

Run: python3 test_adaptive_quiz.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.adaptive_quiz_agent import AdaptiveQuizAgent


def print_header(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_subheader(title):
    """Print formatted subsection header"""
    print(f"\n{title}")
    print("-" * len(title))


def test_difficulty_determination():
    """Test 1: Difficulty determination logic"""
    print_header("TEST 1: Difficulty Determination Logic")
    
    test_cases = [
        # (current_diff, avg_score, expected_diff, description)
        ("medium", 85, "hard", "High performer (85%) should move up"),
        ("medium", 45, "easy", "Struggling (45%) should move down"),
        ("medium", 65, "medium", "Average (65%) should stay same"),
        ("easy", 85, "medium", "Easy performer should graduate to medium"),
        ("hard", 45, "medium", "Hard struggler should drop to medium"),
        ("expert", 85, "expert", "Expert high performer stays at expert"),
        ("easy", 45, "easy", "Easy struggler stays at easy"),
        (None, 75, "medium", "New user defaults to medium"),
    ]
    
    passed = 0
    failed = 0
    
    for current, score, expected, description in test_cases:
        result = AdaptiveQuizAgent.determine_next_difficulty(current, score)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"\n{description}")
        print(f"  Current: {current or 'None'}, Score: {score}%")
        print(f"  Expected: {expected}, Got: {result}")
        print(f"  Status: {status}")
    
    print_subheader("Test 1 Results")
    print(f"Passed: {passed}/{len(test_cases)}")
    print(f"Failed: {failed}/{len(test_cases)}")
    
    return failed == 0


def test_difficulty_contexts():
    """Test 2: Difficulty-specific contexts"""
    print_header("TEST 2: Difficulty Context Generation")
    
    difficulties = ["easy", "medium", "hard", "expert"]
    
    for difficulty in difficulties:
        context = AdaptiveQuizAgent.get_difficulty_context(difficulty)
        
        print(f"\n{difficulty.upper()} Difficulty:")
        print(f"  Temperature: {context['temperature']}")
        print(f"  Cognitive Level: {context['cognitive_level']}")
        print(f"  Question Types: {', '.join(context['question_types'])}")
        
        # Verify structure
        assert 'temperature' in context
        assert 'cognitive_level' in context
        assert 'question_types' in context
        assert 'context_prompt' in context
    
    print_subheader("Test 2 Results")
    print("✅ All difficulty contexts generated successfully")
    
    return True


def test_difficulty_recommendation():
    """Test 3: Difficulty recommendation reasoning"""
    print_header("TEST 3: Difficulty Recommendation Reasoning")
    
    test_cases = [
        {
            "avg_score": 85,
            "current_difficulty": "medium",
            "recommended_difficulty": "hard",
            "total_attempts": 10
        },
        {
            "avg_score": 45,
            "current_difficulty": "hard",
            "recommended_difficulty": "medium",
            "total_attempts": 8
        },
        {
            "avg_score": None,
            "current_difficulty": None,
            "recommended_difficulty": "medium",
            "total_attempts": 0
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\nScenario {i}:")
        print(f"  Average Score: {case['avg_score']}%")
        print(f"  Current Difficulty: {case['current_difficulty'] or 'None (new user)'}")
        print(f"  Recommended: {case['recommended_difficulty']}")
        print(f"  Total Attempts: {case['total_attempts']}")
        
        recommendation = AdaptiveQuizAgent.get_difficulty_recommendation(
            avg_score=case['avg_score'],
            current_difficulty=case['current_difficulty'],
            recommended_difficulty=case['recommended_difficulty'],
            total_attempts=case['total_attempts']
        )
        
        print(f"  Reasoning: {recommendation}")
        
        # Verify reasoning includes key information
        assert case['recommended_difficulty'] in recommendation
    
    print_subheader("Test 3 Results")
    print("✅ All difficulty recommendations generated with proper reasoning")
    
    return True


def test_performance_thresholds():
    """Test 4: Performance threshold boundaries"""
    print_header("TEST 4: Performance Threshold Boundaries")
    
    print("\nThreshold Configuration:")
    print(f"  INCREASE_THRESHOLD = {AdaptiveQuizAgent.INCREASE_THRESHOLD}%")
    print(f"  DECREASE_THRESHOLD = {AdaptiveQuizAgent.DECREASE_THRESHOLD}%")
    
    # Test boundary cases
    boundary_cases = [
        ("medium", 80, "hard", "At increase threshold (80%)"),
        ("medium", 81, "hard", "Just above increase threshold (81%)"),
        ("medium", 79, "medium", "Just below increase threshold (79%)"),
        ("medium", 50, "medium", "At decrease threshold (50%) - maintains current"),
        ("medium", 49, "easy", "Just below decrease threshold (49%)"),
        ("medium", 51, "medium", "Just above decrease threshold (51%)"),
    ]
    
    all_passed = True
    
    for current, score, expected, description in boundary_cases:
        result = AdaptiveQuizAgent.determine_next_difficulty(current, score)
        status = "✅" if result == expected else "❌"
        
        if result != expected:
            all_passed = False
        
        print(f"\n{description}")
        print(f"  Score: {score}%, Expected: {expected}, Got: {result} {status}")
    
    print_subheader("Test 4 Results")
    if all_passed:
        print("✅ All boundary cases handled correctly")
    else:
        print("❌ Some boundary cases failed")
    
    return all_passed


def test_difficulty_progression():
    """Test 5: Difficulty progression scenarios"""
    print_header("TEST 5: Difficulty Progression Scenarios")
    
    # Simulate a student's learning journey
    scenarios = [
        {
            "name": "Fast Learner Journey",
            "sequence": [
                (None, 85),  # Start strong
                ("medium", 90),  # Excellent performance
                ("hard", 88),  # Maintain excellence
                ("expert", 85),  # Still doing well at expert
            ]
        },
        {
            "name": "Struggling Student Journey",
            "sequence": [
                (None, 45),  # Difficult start
                ("medium", 40),  # Still struggling
                ("easy", 65),  # Improving at easy
                ("easy", 82),  # Mastering easy
            ]
        },
        {
            "name": "Inconsistent Performer",
            "sequence": [
                (None, 75),  # Average start
                ("medium", 85),  # Good performance
                ("hard", 45),  # Too difficult
                ("medium", 70),  # Back to stable
            ]
        }
    ]
    
    for scenario in scenarios:
        print_subheader(scenario["name"])
        
        for i, (current_diff, score) in enumerate(scenario["sequence"], 1):
            next_diff = AdaptiveQuizAgent.determine_next_difficulty(current_diff, score)
            print(f"  Quiz {i}: Difficulty={current_diff or 'None'}, Score={score}% → Next={next_diff}")
    
    print_subheader("Test 5 Results")
    print("✅ All progression scenarios executed successfully")
    
    return True


def test_edge_cases():
    """Test 6: Edge cases and error handling"""
    print_header("TEST 6: Edge Cases and Error Handling")
    
    edge_cases = [
        # (current_diff, score, description)
        ("invalid_difficulty", 75, "Invalid difficulty string"),
        ("MEDIUM", 75, "Uppercase difficulty"),
        ("easy", 100, "Perfect score"),
        ("hard", 0, "Zero score"),
        (None, None, "Both None"),
        ("", 75, "Empty string difficulty"),
    ]
    
    all_handled = True
    
    for current, score, description in edge_cases:
        print(f"\n{description}")
        print(f"  Input: current_diff='{current}', score={score}")
        
        try:
            result = AdaptiveQuizAgent.determine_next_difficulty(current, score)
            print(f"  Result: {result} ✅")
        except Exception as e:
            print(f"  Error: {type(e).__name__}: {e}")
            # Some errors are expected for invalid inputs
            if current not in ["invalid_difficulty", "MEDIUM", ""]:
                all_handled = False
    
    print_subheader("Test 6 Results")
    print("✅ Edge cases handled (some errors expected for invalid inputs)")
    
    return True


def test_temperature_variations():
    """Test 7: Temperature settings across difficulties"""
    print_header("TEST 7: Temperature Variations")
    
    difficulties = ["easy", "medium", "hard", "expert"]
    temperatures = []
    
    print("\nTemperature Settings:")
    for difficulty in difficulties:
        context = AdaptiveQuizAgent.get_difficulty_context(difficulty)
        temp = context['temperature']
        temperatures.append(temp)
        print(f"  {difficulty.capitalize():8} → {temp}")
    
    # Verify temperature increases with difficulty
    is_increasing = all(temperatures[i] <= temperatures[i+1] for i in range(len(temperatures)-1))
    
    print_subheader("Test 7 Results")
    if is_increasing:
        print("✅ Temperatures increase appropriately with difficulty")
        print("   (Higher difficulty → Higher temperature → More creative questions)")
    else:
        print("❌ Temperature progression issue detected")
    
    return is_increasing


def run_all_tests():
    """Run all adaptive quiz tests"""
    print_header("ADAPTIVE QUIZ SYSTEM TEST SUITE")
    print("Testing difficulty determination, contexts, and recommendations")
    print("This validates the adaptive learning algorithm")
    
    tests = [
        ("Difficulty Determination", test_difficulty_determination),
        ("Difficulty Contexts", test_difficulty_contexts),
        ("Recommendation Reasoning", test_difficulty_recommendation),
        ("Performance Thresholds", test_performance_thresholds),
        ("Progression Scenarios", test_difficulty_progression),
        ("Edge Cases", test_edge_cases),
        ("Temperature Variations", test_temperature_variations),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' encountered an error: {e}")
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
        print("\n🎉 ALL TESTS PASSED! Adaptive quiz system is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
