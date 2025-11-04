#!/usr/bin/env python3
"""
Test script for the Quiz Agent
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.quiz_agent import generate_quiz_with_fallback, generate_quiz_from_topic
from dotenv import load_dotenv

load_dotenv()


async def test_quiz_agent():
    """Test the quiz agent with sample notes"""
    
    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set in .env file")
        print("\nTo get an API key:")
        print("1. Visit https://openrouter.ai/")
        print("2. Sign up for a free account")
        print("3. Go to https://openrouter.ai/keys")
        print("4. Create a new API key")
        print("5. Add it to backend/.env file")
        return
    
    print("✓ OpenRouter API key found")
    print("\n" + "="*70)
    print("Testing Quiz Agent - Question Generator")
    print("="*70 + "\n")
    
    # Sample notes
    notes = """
    Topic: Python Functions
    
    Summary: Functions are reusable blocks of code that perform specific tasks.
    They help organize code and make it more maintainable.
    
    Key Points:
    1. Functions are defined using the 'def' keyword
    2. Functions can accept parameters (inputs)
    3. Functions can return values using the 'return' statement
    4. Functions promote code reusability and organization
    5. You can call a function by using its name followed by parentheses
    """
    
    print("Sample Study Notes:")
    print("-" * 70)
    print(notes)
    print("-" * 70)
    print("\nGenerating 5 quiz questions... (this may take 10-15 seconds)\n")
    
    try:
        # Generate quiz
        questions = await generate_quiz_with_fallback(notes, num_questions=5)
        
        # Display results
        print("✅ SUCCESS!\n")
        print("="*70)
        print(f"Generated {len(questions)} Quiz Questions")
        print("="*70 + "\n")
        
        for i, q in enumerate(questions, 1):
            print(f"Question {i}:")
            print(f"{q['question']}\n")
            
            for option in q['options']:
                print(f"  {option}")
            
            print(f"\n✓ Correct Answer: {q['answer']}")
            if q.get('explanation'):
                print(f"  Explanation: {q['explanation']}")
            print("\n" + "-"*70 + "\n")
        
        print("="*70)
        print("✅ Quiz Agent is working correctly!")
        print("="*70)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("1. Your OpenRouter API key is valid")
        print("2. You have internet connection")
        print("3. OpenRouter service is available")


async def test_quiz_from_topic():
    """Test generating quiz from structured notes"""
    
    print("\n" + "="*70)
    print("Testing Quiz from Structured Notes")
    print("="*70 + "\n")
    
    topic = "JavaScript Promises"
    summary = "Promises are objects representing the eventual completion or failure of an asynchronous operation."
    key_points = [
        "A Promise can be in one of three states: pending, fulfilled, or rejected",
        "Use .then() to handle successful promise resolution",
        "Use .catch() to handle promise rejection",
        "Promises can be chained for sequential async operations",
        "async/await syntax provides a cleaner way to work with promises"
    ]
    
    print(f"Topic: {topic}")
    print(f"Summary: {summary}")
    print("\nKey Points:")
    for i, point in enumerate(key_points, 1):
        print(f"{i}. {point}")
    
    print("\nGenerating quiz...\n")
    
    try:
        questions = await generate_quiz_from_topic(topic, summary, key_points, num_questions=3)
        
        print("✅ Generated 3 questions:\n")
        for i, q in enumerate(questions, 1):
            print(f"{i}. {q['question']}")
            print(f"   Answer: {q['answer']}\n")
        
        print("✅ Structured notes quiz generation working!")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_quiz_agent())
    asyncio.run(test_quiz_from_topic())
