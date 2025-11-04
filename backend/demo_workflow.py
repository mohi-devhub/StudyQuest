#!/usr/bin/env python3
"""
Complete workflow demo: Generate notes → Generate quiz
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.research_agent import generate_notes_with_fallback
from agents.quiz_agent import generate_quiz_from_topic
from dotenv import load_dotenv

load_dotenv()


async def complete_study_workflow(topic: str):
    """
    Demonstrate the complete StudyQuest workflow:
    1. Generate study notes from a topic
    2. Generate quiz questions from those notes
    """
    
    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not set in .env file")
        return
    
    print("="*70)
    print("StudyQuest Complete Workflow Demo")
    print("="*70)
    print(f"\n📚 Topic: {topic}\n")
    
    # Step 1: Generate study notes
    print("Step 1: Generating study notes...")
    print("-"*70)
    
    try:
        notes = await generate_notes_with_fallback(topic)
        
        print(f"\n✅ Notes Generated!\n")
        print(f"TOPIC: {notes['topic']}")
        print(f"\nSUMMARY:")
        print(f"{notes['summary']}\n")
        print("KEY POINTS:")
        for i, point in enumerate(notes['key_points'], 1):
            print(f"{i}. {point}")
        
        # Step 2: Generate quiz from notes
        print("\n" + "="*70)
        print("Step 2: Generating quiz questions from notes...")
        print("-"*70 + "\n")
        
        quiz = await generate_quiz_from_topic(
            topic=notes['topic'],
            summary=notes['summary'],
            key_points=notes['key_points'],
            num_questions=5
        )
        
        print(f"✅ Quiz Generated! ({len(quiz)} questions)\n")
        print("="*70)
        print("QUIZ QUESTIONS")
        print("="*70 + "\n")
        
        for i, q in enumerate(quiz, 1):
            print(f"Question {i}:")
            print(f"{q['question']}\n")
            
            for option in q['options']:
                # Highlight correct answer
                if option.startswith(q['answer']):
                    print(f"  ✓ {option}")
                else:
                    print(f"    {option}")
            
            print(f"\nCorrect Answer: {q['answer']}")
            if q.get('explanation'):
                print(f"Explanation: {q['explanation']}")
            print("\n" + "-"*70 + "\n")
        
        # Summary
        print("="*70)
        print("✅ WORKFLOW COMPLETED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"  - Topic: {topic}")
        print(f"  - Key Points Generated: {len(notes['key_points'])}")
        print(f"  - Quiz Questions Generated: {len(quiz)}")
        print(f"  - Ready for studying! 🎓")
        print("\n" + "="*70)
        
        return {
            "notes": notes,
            "quiz": quiz
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("1. Your OpenRouter API key is valid")
        print("2. You have internet connection")
        print("3. OpenRouter service is available")
        return None


async def main():
    """Run workflow demos with different topics"""
    
    topics = [
        "Python List Comprehensions",
        # Uncomment to try more topics:
        # "REST API Design Principles",
        # "Git Branching Strategies",
    ]
    
    for topic in topics:
        result = await complete_study_workflow(topic)
        if result:
            print("\n\n")  # Space between multiple topics


if __name__ == "__main__":
    asyncio.run(main())
