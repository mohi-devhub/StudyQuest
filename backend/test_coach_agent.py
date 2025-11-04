#!/usr/bin/env python3
"""
Test the Coach Agent - Workflow Coordinator
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.coach_agent import (
    study_topic, 
    study_multiple_topics,
    get_study_progress
)
from dotenv import load_dotenv

load_dotenv()


async def test_basic_workflow():
    """Test the basic study workflow."""
    print("\n" + "="*70)
    print("TEST 1: Basic Study Workflow")
    print("="*70)
    
    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set in .env file")
        return False
    
    print("✓ OpenRouter API key found\n")
    
    try:
        # Test with a simple topic
        topic = "Recursion in Programming"
        result = await study_topic(topic, num_questions=3)
        
        print("\n" + "="*70)
        print("STUDY PACKAGE GENERATED")
        print("="*70)
        
        print(f"\n📚 TOPIC: {result['topic']}")
        print(f"\n📝 SUMMARY:")
        print(f"{result['notes']['summary']}")
        
        print(f"\n🔑 KEY POINTS ({len(result['notes']['key_points'])}):")
        for i, point in enumerate(result['notes']['key_points'], 1):
            print(f"{i}. {point}")
        
        print(f"\n❓ QUIZ QUESTIONS ({len(result['quiz'])}):")
        for i, q in enumerate(result['quiz'], 1):
            print(f"\nQ{i}: {q['question']}")
            for option in q['options']:
                marker = "✓" if option.startswith(q['answer']) else " "
                print(f"  {marker} {option}")
        
        print("\n" + "="*70)
        print("✅ TEST 1 PASSED: Basic workflow working!")
        print("="*70)
        
        return result
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_progress_tracking(study_package):
    """Test progress tracking with quiz answers."""
    if not study_package:
        print("\n⏭️  Skipping TEST 2: No study package available")
        return
    
    print("\n\n" + "="*70)
    print("TEST 2: Progress Tracking")
    print("="*70)
    
    try:
        # Simulate user answers (mix of correct and incorrect)
        num_questions = len(study_package['quiz'])
        
        # Get correct answers
        correct_answers = [q['answer'] for q in study_package['quiz']]
        
        # Simulate 2 correct, 1 wrong for a 3-question quiz
        if num_questions >= 3:
            user_answers = [
                correct_answers[0],  # Correct
                correct_answers[1],  # Correct
                "A" if correct_answers[2] != "A" else "B"  # Wrong
            ]
        else:
            user_answers = correct_answers[:num_questions]
        
        print(f"\nSimulating quiz attempt with {num_questions} questions...")
        print(f"User answers: {user_answers}")
        print(f"Correct answers: {correct_answers}")
        
        # Get progress report
        progress = await get_study_progress(study_package, user_answers)
        
        print("\n" + "="*70)
        print("PROGRESS REPORT")
        print("="*70)
        
        print(f"\n📊 Topic: {progress['topic']}")
        print(f"Score: {progress['correct_answers']}/{progress['total_questions']} ({progress['score_percentage']}%)")
        print(f"Feedback: {progress['feedback']}")
        
        print("\n📝 Detailed Results:")
        for result in progress['results']:
            status = "✅" if result['is_correct'] else "❌"
            print(f"\n{status} Q{result['question_number']}: {result['question']}")
            print(f"   Your answer: {result['user_answer']} | Correct: {result['correct_answer']}")
            if not result['is_correct'] and result['explanation']:
                print(f"   💡 {result['explanation']}")
        
        print("\n" + "="*70)
        print("✅ TEST 2 PASSED: Progress tracking working!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_multiple_topics():
    """Test processing multiple topics."""
    print("\n\n" + "="*70)
    print("TEST 3: Multiple Topics (Parallel Processing)")
    print("="*70)
    
    try:
        topics = [
            "Binary Search Algorithm",
            "HTTP Status Codes"
        ]
        
        print(f"\nProcessing {len(topics)} topics in parallel...")
        results = await study_multiple_topics(topics, num_questions=2)
        
        print("\n" + "="*70)
        print(f"RESULTS: {len(results)} topics processed")
        print("="*70)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['topic']}")
            print(f"   - Key Points: {result['metadata']['num_key_points']}")
            print(f"   - Quiz Questions: {result['metadata']['num_questions']}")
        
        print("\n" + "="*70)
        print("✅ TEST 3 PASSED: Multiple topics working!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("COACH AGENT - COMPREHENSIVE TESTING")
    print("="*70)
    
    # Test 1: Basic workflow
    study_package = await test_basic_workflow()
    
    # Test 2: Progress tracking
    if study_package:
        await test_progress_tracking(study_package)
    
    # Test 3: Multiple topics (commented out to avoid rate limits)
    # await test_multiple_topics()
    
    print("\n\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)
    print("\n💡 Tip: Uncomment test_multiple_topics() in main() to test parallel processing")
    print("   (Warning: May hit rate limits with free tier)\n")


if __name__ == "__main__":
    asyncio.run(main())
