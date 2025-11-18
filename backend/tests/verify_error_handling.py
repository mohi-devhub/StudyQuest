#!/usr/bin/env python3
"""
Quick verification script to demonstrate AI error handling
This can be run manually to verify error handling behavior
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Import agents
from agents.adaptive_quiz_agent import AdaptiveQuizAgent
from agents.recommendation_agent import RecommendationAgent
from datetime import datetime


async def test_empty_notes():
    """Test 1: Empty notes handling"""
    print("\n" + "="*60)
    print("TEST 1: Empty Notes Handling")
    print("="*60)
    
    try:
        result = await AdaptiveQuizAgent.generate_adaptive_quiz(
            notes="",
            difficulty='medium',
            num_questions=3
        )
        print("❌ FAILED: Should have raised ValueError")
    except ValueError as e:
        print(f"✅ PASSED: Caught ValueError as expected")
        print(f"   Error message: {str(e)}")
    except Exception as e:
        print(f"⚠️  UNEXPECTED: Got {type(e).__name__}: {str(e)}")


async def test_missing_api_key():
    """Test 2: Missing API key handling"""
    print("\n" + "="*60)
    print("TEST 2: Missing API Key Handling")
    print("="*60)
    
    # Save original key
    original_key = os.getenv('OPENROUTER_API_KEY')
    
    try:
        # Remove API key
        if 'OPENROUTER_API_KEY' in os.environ:
            del os.environ['OPENROUTER_API_KEY']
        
        notes = "Test notes about Python programming"
        
        result = await AdaptiveQuizAgent.generate_adaptive_quiz(
            notes=notes,
            difficulty='medium',
            num_questions=2
        )
        print("❌ FAILED: Should have raised ValueError")
        
    except ValueError as e:
        error_msg = str(e)
        if 'OPENROUTER_API_KEY' in error_msg:
            print(f"✅ PASSED: Caught ValueError with clear message")
            print(f"   Error message: {error_msg}")
        else:
            print(f"⚠️  PARTIAL: Caught ValueError but message unclear")
            print(f"   Error message: {error_msg}")
    except Exception as e:
        print(f"⚠️  UNEXPECTED: Got {type(e).__name__}: {str(e)}")
    finally:
        # Restore original key
        if original_key:
            os.environ['OPENROUTER_API_KEY'] = original_key


async def test_recommendation_fallback():
    """Test 3: Recommendation fallback on API failure"""
    print("\n" + "="*60)
    print("TEST 3: Recommendation Fallback (Invalid API Key)")
    print("="*60)
    
    # Save original key
    original_key = os.getenv('OPENROUTER_API_KEY')
    
    try:
        # Set invalid API key
        os.environ['OPENROUTER_API_KEY'] = 'invalid_test_key_12345'
        
        recent_date = datetime.now().isoformat()
        user_progress = [
            {
                'topic': 'Python',
                'avg_score': 60.0,
                'total_attempts': 3,
                'last_attempt': recent_date
            }
        ]
        
        result = await RecommendationAgent.get_study_recommendations(
            user_progress=user_progress,
            max_recommendations=3,
            include_ai_insights=True
        )
        
        # Check if recommendations were returned
        if 'recommendations' in result and len(result['recommendations']) > 0:
            print(f"✅ PASSED: Recommendations returned despite invalid API key")
            print(f"   Recommendations count: {len(result['recommendations'])}")
            print(f"   AI enhanced: {result.get('ai_enhanced', False)}")
            
            if result.get('ai_enhanced') == False:
                print(f"   ✅ Correctly disabled AI enhancement")
            else:
                print(f"   ⚠️  AI enhancement should be disabled")
        else:
            print(f"❌ FAILED: No recommendations returned")
            
    except Exception as e:
        print(f"⚠️  UNEXPECTED: Got {type(e).__name__}: {str(e)}")
    finally:
        # Restore original key
        if original_key:
            os.environ['OPENROUTER_API_KEY'] = original_key


async def test_valid_quiz_generation():
    """Test 4: Valid quiz generation (baseline)"""
    print("\n" + "="*60)
    print("TEST 4: Valid Quiz Generation (Baseline)")
    print("="*60)
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  SKIPPED: OPENROUTER_API_KEY not set")
        return
    
    try:
        notes = """
        Topic: Python Functions
        
        Summary: Functions are reusable blocks of code that perform specific tasks.
        
        Key Points:
        1. Functions are defined using the def keyword
        2. Functions can accept parameters
        3. Functions can return values
        4. Functions help organize code
        """
        
        result = await AdaptiveQuizAgent.generate_adaptive_quiz(
            notes=notes,
            difficulty='easy',
            num_questions=2
        )
        
        if 'questions' in result and len(result['questions']) == 2:
            print(f"✅ PASSED: Quiz generated successfully")
            print(f"   Questions count: {len(result['questions'])}")
            print(f"   Difficulty: {result.get('difficulty')}")
            
            # Validate structure
            for i, q in enumerate(result['questions'], 1):
                has_question = 'question' in q
                has_options = 'options' in q and len(q['options']) == 4
                has_answer = 'answer' in q and q['answer'] in ['A', 'B', 'C', 'D']
                
                if has_question and has_options and has_answer:
                    print(f"   ✅ Question {i}: Valid structure")
                else:
                    print(f"   ❌ Question {i}: Invalid structure")
        else:
            print(f"❌ FAILED: Invalid quiz structure")
            
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {str(e)}")


async def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("AI ERROR HANDLING VERIFICATION")
    print("="*60)
    print("\nThis script demonstrates the error handling capabilities")
    print("of the StudyQuest AI agents.\n")
    
    # Run tests
    await test_empty_notes()
    await test_missing_api_key()
    await test_recommendation_fallback()
    await test_valid_quiz_generation()
    
    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    print("\nSummary:")
    print("- Empty notes are rejected with clear error")
    print("- Missing API key is detected with informative message")
    print("- Recommendations fallback gracefully on API failure")
    print("- Valid requests work as expected (when API key is set)")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
