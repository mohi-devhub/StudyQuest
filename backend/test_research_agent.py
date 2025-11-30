#!/usr/bin/env python3
"""
Test script for the Research Agent
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.research_agent import generate_notes_with_fallback
from dotenv import load_dotenv

load_dotenv()


async def test_research_agent():
    """Test the research agent with a sample topic"""
    
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in .env file")
        print("\nTo get an API key:")
        print("1. Visit https://makersuite.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Create a new API key")
        print("4. Add it to backend/.env file")
        return
    
    print("✓ OpenRouter API key found")
    print("\n" + "="*60)
    print("Testing Research Agent - Notes Generator")
    print("="*60 + "\n")
    
    # Test topic
    topic = "Python Functions"
    print(f"Topic: {topic}\n")
    print("Generating notes... (this may take 5-10 seconds)\n")
    
    try:
        # Generate notes
        notes = await generate_notes_with_fallback(topic)
        
        # Display results
        print("✅ SUCCESS!\n")
        print("="*60)
        print(f"TOPIC: {notes['topic']}")
        print("="*60)
        print(f"\nSUMMARY:")
        print(f"{notes['summary']}\n")
        print("KEY POINTS:")
        for i, point in enumerate(notes['key_points'], 1):
            print(f"{i}. {point}")
        print("\n" + "="*60)
        print("✅ Research Agent is working correctly!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print("\nPlease check:")
        print("1. Your OpenRouter API key is valid")
        print("2. You have internet connection")
        print("3. OpenRouter service is available")


if __name__ == "__main__":
    asyncio.run(test_research_agent())
