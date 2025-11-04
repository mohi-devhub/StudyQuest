"""
Coach Agent - Workflow Coordinator for StudyQuest

This agent coordinates the Research Agent and Quiz Agent to create
a complete study workflow using CrewAI for multi-agent orchestration.
"""

import asyncio
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Optional imports for CrewAI integration (if available)
try:
    from crewai import Agent, Task, Crew, Process
    from langchain_core.tools import Tool
    from langchain_openai import ChatOpenAI
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    print("⚠️  CrewAI not available. Using simplified workflow coordination.")

from .research_agent import generate_notes_with_fallback, generate_notes
from .quiz_agent import generate_quiz_with_fallback, generate_quiz

load_dotenv()

# OpenRouter LLM configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def get_openrouter_llm(model: str = "google/gemini-2.0-flash-exp:free"):
    """Get configured OpenRouter LLM for CrewAI agents."""
    if not CREWAI_AVAILABLE:
        raise ImportError("CrewAI and LangChain are required for this function. Install with: pip install crewai langchain-openai")
    
    return ChatOpenAI(
        model=model,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base=OPENROUTER_BASE_URL,
        temperature=0.7,
        default_headers={
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "StudyQuest"
        }
    )


def sync_generate_notes(topic: str) -> str:
    """Synchronous wrapper for the research agent (for CrewAI compatibility)."""
    if not CREWAI_AVAILABLE:
        raise ImportError("CrewAI integration requires crewai package")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(generate_notes_with_fallback(topic))
        # Convert to formatted string for the agent
        formatted = f"""Topic: {result['topic']}

Summary:
{result['summary']}

Key Points:
"""
        for i, point in enumerate(result['key_points'], 1):
            formatted += f"{i}. {point}\n"
        
        return formatted
    finally:
        loop.close()


def sync_generate_quiz(notes: str, num_questions: int = 5) -> str:
    """Synchronous wrapper for the quiz agent (for CrewAI compatibility)."""
    if not CREWAI_AVAILABLE:
        raise ImportError("CrewAI integration requires crewai package")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(generate_quiz_with_fallback(notes, num_questions))
        # Convert to formatted string for the agent
        formatted = "Quiz Questions:\n\n"
        for i, q in enumerate(result, 1):
            formatted += f"Q{i}: {q['question']}\n"
            for option in q['options']:
                formatted += f"  {option}\n"
            formatted += f"Answer: {q['answer']}\n"
            if q.get('explanation'):
                formatted += f"Explanation: {q['explanation']}\n"
            formatted += "\n"
        
        return formatted
    finally:
        loop.close()


async def study_topic(topic: str, num_questions: int = 5) -> Dict:
    """
    Coordinate a complete study workflow for a given topic.
    
    This is the simplified version that directly calls the agents
    without CrewAI orchestration.
    
    Args:
        topic: The topic to study
        num_questions: Number of quiz questions to generate
        
    Returns:
        dict: Complete study package with notes and quiz
    """
    print(f"\n🎓 Starting study workflow for: {topic}")
    print("="*70)
    
    # Step 1: Generate study notes
    print("\n📚 Step 1: Generating study notes...")
    notes = await generate_notes_with_fallback(topic)
    
    print(f"✅ Generated notes with {len(notes['key_points'])} key points")
    
    # Step 2: Format notes for quiz generation
    formatted_notes = f"""Topic: {notes['topic']}

Summary: {notes['summary']}

Key Points:
"""
    for i, point in enumerate(notes['key_points'], 1):
        formatted_notes += f"{i}. {point}\n"
    
    # Step 3: Generate quiz questions
    print(f"\n📝 Step 2: Generating {num_questions} quiz questions...")
    quiz = await generate_quiz_with_fallback(formatted_notes, num_questions)
    
    print(f"✅ Generated {len(quiz)} quiz questions")
    
    # Return complete study package
    print("\n✅ Study workflow completed successfully!")
    print("="*70)
    
    return {
        "topic": notes['topic'],
        "notes": notes,
        "quiz": quiz,
        "metadata": {
            "num_key_points": len(notes['key_points']),
            "num_questions": len(quiz)
        }
    }


async def study_topic_with_crewai(topic: str, num_questions: int = 5) -> Dict:
    """
    Coordinate a complete study workflow using CrewAI multi-agent system.
    
    This version uses CrewAI to orchestrate the Research and Quiz agents
    with proper agent definitions, tools, and tasks.
    
    Args:
        topic: The topic to study
        num_questions: Number of quiz questions to generate
        
    Returns:
        dict: Complete study package with notes and quiz
    """
    if not CREWAI_AVAILABLE:
        print("⚠️  CrewAI not available. Falling back to simplified workflow.")
        return await study_topic(topic, num_questions)
    
    print(f"\n🎓 Starting CrewAI study workflow for: {topic}")
    print("="*70)
    
    # Get LLM for agents
    llm = get_openrouter_llm()
    
    # Define tools for agents
    research_tool = Tool(
        name="generate_study_notes",
        func=sync_generate_notes,
        description="Generates comprehensive study notes for a given topic. Input should be the topic name."
    )
    
    quiz_tool = Tool(
        name="generate_quiz_questions",
        func=lambda notes: sync_generate_quiz(notes, num_questions),
        description="Generates quiz questions from study notes. Input should be the formatted study notes."
    )
    
    # Define Research Agent
    research_agent = Agent(
        role="Research Specialist",
        goal=f"Generate comprehensive, well-structured study notes on {topic}",
        backstory="""You are an expert educational content creator specializing in 
        breaking down complex topics into clear, digestible study notes. You excel 
        at identifying key concepts and presenting them in a student-friendly manner.""",
        tools=[research_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Define Quiz Agent
    quiz_agent = Agent(
        role="Assessment Specialist",
        goal=f"Create effective quiz questions to test understanding of {topic}",
        backstory="""You are an expert in educational assessment and question design.
        You create challenging but fair multiple-choice questions that test deep 
        understanding rather than rote memorization.""",
        tools=[quiz_tool],
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Define Coach Agent (Coordinator)
    coach_agent = Agent(
        role="Study Coach",
        goal="Coordinate the creation of a complete study package",
        backstory="""You are a master educator who coordinates different specialists
        to create the best learning experience. You ensure that study materials and
        assessments are aligned and comprehensive.""",
        llm=llm,
        verbose=True,
        allow_delegation=True
    )
    
    # Define Tasks
    research_task = Task(
        description=f"""Generate comprehensive study notes for the topic: {topic}.
        The notes should include:
        1. A clear, concise summary
        2. 5-7 key points covering the most important concepts
        3. Well-organized and easy to understand content
        
        Use the generate_study_notes tool to create the notes.""",
        agent=research_agent,
        expected_output="Formatted study notes with topic, summary, and key points"
    )
    
    quiz_task = Task(
        description=f"""Based on the study notes generated, create {num_questions} 
        multiple-choice quiz questions. Each question should:
        1. Test understanding of key concepts
        2. Have 4 options (A, B, C, D)
        3. Have one correct answer
        4. Include an explanation
        
        Use the generate_quiz_questions tool with the study notes as input.""",
        agent=quiz_agent,
        expected_output=f"{num_questions} well-designed quiz questions with options and explanations"
    )
    
    coordination_task = Task(
        description=f"""Coordinate the complete study workflow for {topic}:
        1. Ensure high-quality study notes are generated
        2. Ensure quiz questions align with the notes
        3. Verify the complete study package is ready
        
        The final output should be a complete study package ready for students.""",
        agent=coach_agent,
        expected_output="Confirmation that both study notes and quiz are complete and aligned"
    )
    
    # Create Crew with sequential process
    crew = Crew(
        agents=[research_agent, quiz_agent, coach_agent],
        tasks=[research_task, quiz_task, coordination_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the crew
    print("\n🚀 Executing CrewAI workflow...")
    result = crew.kickoff()
    
    print("\n✅ CrewAI workflow completed!")
    print("="*70)
    
    # For now, fall back to direct implementation to get structured data
    # CrewAI result is text-based, so we'll run our agents directly
    notes = await generate_notes_with_fallback(topic)
    
    formatted_notes = f"""Topic: {notes['topic']}

Summary: {notes['summary']}

Key Points:
"""
    for i, point in enumerate(notes['key_points'], 1):
        formatted_notes += f"{i}. {point}\n"
    
    quiz = await generate_quiz_with_fallback(formatted_notes, num_questions)
    
    return {
        "topic": notes['topic'],
        "notes": notes,
        "quiz": quiz,
        "metadata": {
            "num_key_points": len(notes['key_points']),
            "num_questions": len(quiz),
            "crewai_output": str(result)
        }
    }


async def study_multiple_topics(topics: List[str], num_questions: int = 5) -> List[Dict]:
    """
    Process multiple topics in parallel.
    
    Args:
        topics: List of topics to study
        num_questions: Number of quiz questions per topic
        
    Returns:
        list: List of study packages, one per topic
    """
    print(f"\n🎓 Processing {len(topics)} topics...")
    print("="*70)
    
    # Process all topics concurrently
    tasks = [study_topic(topic, num_questions) for topic in topics]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out any errors
    successful_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Error processing '{topics[i]}': {str(result)}")
        else:
            successful_results.append(result)
    
    print(f"\n✅ Successfully processed {len(successful_results)}/{len(topics)} topics")
    print("="*70)
    
    return successful_results


async def get_study_progress(study_package: Dict, quiz_answers: List[str]) -> Dict:
    """
    Evaluate quiz answers and provide progress feedback.
    
    Args:
        study_package: The study package from study_topic()
        quiz_answers: List of user's answers (e.g., ["A", "B", "C", "D", "A"])
        
    Returns:
        dict: Progress report with score and feedback
    """
    quiz = study_package['quiz']
    
    if len(quiz_answers) != len(quiz):
        raise ValueError(f"Expected {len(quiz)} answers, got {len(quiz_answers)}")
    
    correct_count = 0
    results = []
    
    for i, (question, answer) in enumerate(zip(quiz, quiz_answers)):
        is_correct = answer.upper() == question['answer'].upper()
        if is_correct:
            correct_count += 1
        
        results.append({
            "question_number": i + 1,
            "question": question['question'],
            "user_answer": answer.upper(),
            "correct_answer": question['answer'],
            "is_correct": is_correct,
            "explanation": question.get('explanation', '')
        })
    
    score_percentage = (correct_count / len(quiz)) * 100
    
    # Generate feedback based on score
    if score_percentage >= 90:
        feedback = "Excellent! You have mastered this topic! 🌟"
    elif score_percentage >= 70:
        feedback = "Great job! You have a solid understanding. 👍"
    elif score_percentage >= 50:
        feedback = "Good effort! Review the explanations to improve. 📚"
    else:
        feedback = "Keep studying! Review the notes and try again. 💪"
    
    return {
        "topic": study_package['topic'],
        "total_questions": len(quiz),
        "correct_answers": correct_count,
        "score_percentage": round(score_percentage, 1),
        "feedback": feedback,
        "results": results
    }


# Export main functions
__all__ = [
    'study_topic',
    'study_topic_with_crewai',
    'study_multiple_topics',
    'get_study_progress',
]
