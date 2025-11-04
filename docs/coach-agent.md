# Coach Agent - Workflow Coordinator

## Overview

The Coach Agent is the intelligent workflow coordinator for StudyQuest. It orchestrates the Research Agent and Quiz Agent to create complete study packages through a seamless, automated workflow.

## Features

### 🎯 Core Capabilities

1. **Workflow Coordination**
   - Automatically sequences Research → Quiz generation
   - Handles errors and retries with multiple AI models
   - Provides progress tracking and feedback

2. **Study Package Creation**
   - `study_topic(topic, num_questions)` - Complete study workflow
   - Returns structured data: notes + quiz + metadata
   - Optimized for single topics

3. **Batch Processing**
   - `study_multiple_topics(topics, num_questions)` - Parallel processing
   - Efficient for multiple topics at once
   - Error handling for individual topic failures

4. **Progress Tracking**
   - `get_study_progress(study_package, answers)` - Quiz evaluation
   - Calculates score percentage
   - Provides personalized feedback
   - Detailed per-question analysis

5. **CrewAI Integration (Optional)**
   - `study_topic_with_crewai()` - Advanced multi-agent orchestration
   - Requires: `pip install crewai langchain-openai`
   - Falls back to simplified workflow if not available

## Architecture

```
Coach Agent (Coordinator)
    ├── Research Agent (Notes Generator)
    │   └── OpenRouter API → AI Models
    ├── Quiz Agent (Question Generator)
    │   └── OpenRouter API → AI Models
    └── Progress Tracker
        └── Answer Evaluation
```

## Usage Examples

### Basic Study Workflow

```python
from agents.coach_agent import study_topic
import asyncio

async def main():
    # Generate complete study package
    result = await study_topic(
        topic="Python Decorators",
        num_questions=5
    )
    
    # Access the results
    print(f"Topic: {result['topic']}")
    print(f"Summary: {result['notes']['summary']}")
    print(f"Key Points: {len(result['notes']['key_points'])}")
    print(f"Quiz Questions: {len(result['quiz'])}")

asyncio.run(main())
```

### Multiple Topics (Parallel)

```python
from agents.coach_agent import study_multiple_topics

async def batch_study():
    topics = [
        "REST API Design",
        "GraphQL Basics",
        "WebSocket Protocol"
    ]
    
    results = await study_multiple_topics(topics, num_questions=3)
    
    for package in results:
        print(f"✅ {package['topic']}: {len(package['quiz'])} questions")

asyncio.run(batch_study())
```

### Progress Tracking

```python
from agents.coach_agent import study_topic, get_study_progress

async def study_and_quiz():
    # 1. Generate study package
    package = await study_topic("Git Branching", num_questions=5)
    
    # 2. Student takes quiz (simulated)
    answers = ["A", "B", "C", "D", "A"]
    
    # 3. Get progress report
    progress = await get_study_progress(package, answers)
    
    print(f"Score: {progress['score_percentage']}%")
    print(f"Feedback: {progress['feedback']}")
    
    # Review wrong answers
    for result in progress['results']:
        if not result['is_correct']:
            print(f"❌ Q{result['question_number']}: {result['question']}")
            print(f"   Your answer: {result['user_answer']}")
            print(f"   Correct: {result['correct_answer']}")
            print(f"   💡 {result['explanation']}")

asyncio.run(study_and_quiz())
```

## API Reference

### `study_topic(topic: str, num_questions: int = 5) -> Dict`

Creates a complete study package for a single topic.

**Parameters:**
- `topic` (str): The subject to study
- `num_questions` (int): Number of quiz questions (default: 5, range: 1-20)

**Returns:**
```python
{
    "topic": "Python Decorators",
    "notes": {
        "topic": "Python Decorators",
        "summary": "...",
        "key_points": ["...", "...", ...]
    },
    "quiz": [
        {
            "question": "What is a decorator?",
            "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
            "answer": "B",
            "explanation": "..."
        },
        # ... more questions
    ],
    "metadata": {
        "num_key_points": 7,
        "num_questions": 5
    }
}
```

### `study_multiple_topics(topics: List[str], num_questions: int = 5) -> List[Dict]`

Process multiple topics in parallel.

**Parameters:**
- `topics` (List[str]): List of topics to study
- `num_questions` (int): Questions per topic (default: 5)

**Returns:**
List of study packages (same structure as `study_topic`)

**Note:** Failed topics are logged but don't stop other topics from processing.

### `get_study_progress(study_package: Dict, quiz_answers: List[str]) -> Dict`

Evaluate quiz answers and generate progress report.

**Parameters:**
- `study_package` (Dict): Result from `study_topic()`
- `quiz_answers` (List[str]): Student's answers (e.g., `["A", "B", "C"]`)

**Returns:**
```python
{
    "topic": "Python Decorators",
    "total_questions": 5,
    "correct_answers": 4,
    "score_percentage": 80.0,
    "feedback": "Great job! You have a solid understanding. 👍",
    "results": [
        {
            "question_number": 1,
            "question": "What is...",
            "user_answer": "A",
            "correct_answer": "A",
            "is_correct": True,
            "explanation": "..."
        },
        # ... more results
    ]
}
```

**Feedback Tiers:**
- 90%+ → "Excellent! You have mastered this topic! 🌟"
- 70-89% → "Great job! You have a solid understanding. 👍"
- 50-69% → "Good effort! Review the explanations to improve. 📚"
- <50% → "Keep studying! Review the notes and try again. 💪"

## CrewAI Integration

The Coach Agent supports advanced multi-agent orchestration via CrewAI.

### Installation

```bash
pip install crewai langchain-openai
```

### Usage

```python
from agents.coach_agent import study_topic_with_crewai

async def crewai_workflow():
    result = await study_topic_with_crewai(
        topic="Microservices Architecture",
        num_questions=5
    )
    # Same return structure as study_topic()
    # + metadata.crewai_output with agent logs

asyncio.run(crewai_workflow())
```

### Agent Roles

When using CrewAI, three specialized agents work together:

1. **Research Specialist** - Generates study notes
   - Expert in educational content creation
   - Breaks down complex topics
   - Uses research_agent tools

2. **Assessment Specialist** - Creates quiz questions
   - Expert in question design
   - Tests deep understanding
   - Uses quiz_agent tools

3. **Study Coach** - Coordinates the workflow
   - Master educator
   - Ensures quality and alignment
   - Delegates to specialists

## Integration with Routes

The Coach Agent is integrated into the API routes:

### Study Routes (`/study`)

```python
# backend/routes/study.py
from agents.coach_agent import study_topic

@router.post("/study/complete")
async def complete_study_workflow(request: StudyRequest):
    result = await study_topic(
        topic=request.topic,
        num_questions=request.num_questions
    )
    return result
```

### Progress Routes (`/progress`)

```python
# backend/routes/progress.py
from agents.coach_agent import get_study_progress

@router.post("/progress/evaluate")
async def evaluate_quiz(request: EvaluationRequest):
    progress = await get_study_progress(
        study_package=request.study_package,
        quiz_answers=request.answers
    )
    return progress
```

## Error Handling

The Coach Agent implements robust error handling:

### Model Fallback Chain
```python
models = [
    "google/gemini-2.0-flash-exp:free",      # Primary
    "meta-llama/llama-3.2-3b-instruct:free", # Backup 1
    "meta-llama/llama-3.2-1b-instruct:free", # Backup 2
    "qwen/qwen-2.5-7b-instruct:free",        # Backup 3
    "microsoft/phi-3-mini-128k-instruct:free" # Backup 4
]
```

### Common Issues

**Rate Limiting (429)**
- Free tier has limited requests/minute
- Solution: Wait 1-2 minutes or add your own API key
- Alternative: Use paid OpenRouter credits

**Model Unavailable (404)**
- Free tier models occasionally rotate
- Solution: Model fallback automatically tries alternatives
- Update model list if persistent failures

**Network Errors (500)**
- Temporary OpenRouter issues
- Solution: Retry or wait a few minutes
- Check OpenRouter status page

## Performance Considerations

### Single Topic
- Average time: 15-25 seconds
- Notes generation: 8-12 seconds
- Quiz generation: 7-13 seconds

### Multiple Topics (Parallel)
- 3 topics: ~20-30 seconds (vs 60-75 sequential)
- Uses `asyncio.gather()` for concurrency
- Rate limits may apply on free tier

### Optimization Tips

1. **Batch similar topics** - Use `study_multiple_topics()` for efficiency
2. **Cache results** - Store study packages in database
3. **Fewer questions** - 3-5 questions generate faster than 10-20
4. **Use paid models** - Faster, more reliable, higher quality

## Testing

Run the comprehensive test suite:

```bash
cd backend
source venv/bin/activate
python3 test_coach_agent.py
```

**Tests Include:**
- Basic workflow (notes → quiz)
- Progress tracking (quiz evaluation)
- Multiple topics (parallel processing)
- Error handling (rate limits, failures)

## Future Enhancements

- [ ] Spaced repetition scheduling
- [ ] Adaptive difficulty (adjust questions based on performance)
- [ ] Multi-language support
- [ ] Study session analytics
- [ ] Collaborative study groups
- [ ] Export to flashcards (Anki, Quizlet)

## Dependencies

**Required:**
- `httpx` - Async HTTP client
- `python-dotenv` - Environment variables
- Research Agent (`agents.research_agent`)
- Quiz Agent (`agents.quiz_agent`)

**Optional:**
- `crewai` - Advanced multi-agent orchestration
- `langchain-openai` - LLM integration for CrewAI
- `langchain-core` - Tool definitions

## Environment Variables

```bash
# .env file
OPENROUTER_API_KEY=your_key_here
```

Get your API key: [OpenRouter Settings](https://openrouter.ai/settings/keys)

## Related Documentation

- [Research Agent](./research-agent.md) - Notes generation
- [Quiz Agent](./quiz-agent.md) - Question creation
- [API Routes](./quick-start.md#api-endpoints) - HTTP endpoints
- [Supabase Integration](./supabase-setup.md) - Database storage

---

**Last Updated:** November 5, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅
