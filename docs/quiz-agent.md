# Quiz Agent - Question Generator

## Overview

The Quiz Agent generates multiple-choice questions from study notes using OpenRouter's AI models. It creates unique, well-formatted questions with exactly one correct answer per question.

## Features

- ✅ **Multiple Choice Questions** - 4 options (A-D) per question
- ✅ **Question Validation** - Ensures uniqueness and correct formatting
- ✅ **Answer Explanations** - Brief explanation for each correct answer
- ✅ **Flexible Input** - Accept raw notes or structured notes
- ✅ **Automatic Fallback** - Tries multiple AI models if one fails
- ✅ **Configurable** - Choose number of questions (1-20)

## API Endpoints

### 1. Generate Quiz from Raw Notes

**POST** `/quiz/generate`

Generate quiz questions from any text/notes.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request:**
```json
{
  "notes": "Python functions are reusable blocks of code. They use the def keyword. Functions can take parameters and return values.",
  "num_questions": 5
}
```

**Response:**
```json
{
  "questions": [
    {
      "question": "What keyword is used to define a function in Python?",
      "options": [
        "A) function",
        "B) def",
        "C) func",
        "D) define"
      ],
      "answer": "B",
      "explanation": "The 'def' keyword is used to define functions in Python"
    }
  ],
  "total_questions": 5
}
```

### 2. Generate Quiz from Structured Notes

**POST** `/quiz/generate-from-topic`

Generate quiz from topic, summary, and key points (output from research agent).

**Request:**
```json
{
  "topic": "Python Functions",
  "summary": "Functions are reusable blocks of code that perform specific tasks.",
  "key_points": [
    "Functions are defined using the def keyword",
    "They can accept parameters and return values",
    "Functions promote code reusability"
  ],
  "num_questions": 5
}
```

**Response:** Same format as above

## Usage Examples

### cURL

```bash
# Get your token first by logging in
TOKEN="your_jwt_token_here"

# Generate quiz from raw notes
curl -X POST http://localhost:8000/quiz/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "React hooks are functions that let you use state and other React features without writing a class. useState is a Hook that lets you add state to functional components.",
    "num_questions": 3
  }'

# Generate quiz from structured notes
curl -X POST http://localhost:8000/quiz/generate-from-topic \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "React Hooks",
    "summary": "Hooks let you use state and lifecycle features in functional components.",
    "key_points": ["useState for state management", "useEffect for side effects"],
    "num_questions": 3
  }'
```

### Python

```python
import httpx
import asyncio

async def generate_quiz(notes: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/quiz/generate",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "notes": notes,
                "num_questions": 5
            }
        )
        return response.json()

# Usage
token = "your_jwt_token"
quiz = asyncio.run(generate_quiz("Study material here...", token))
print(quiz)
```

### JavaScript/Frontend

```javascript
async function generateQuiz(notes, numQuestions = 5) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/quiz/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ notes, num_questions: numQuestions })
  });
  
  return response.json();
}

// Usage
const quiz = await generateQuiz('Your study notes here...', 5);
console.log(quiz.questions);
```

## Complete Workflow: Notes → Quiz

```javascript
// Step 1: Generate study notes
const notesResponse = await fetch('http://localhost:8000/study/generate-notes', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ topic: 'Machine Learning' })
});
const notes = await notesResponse.json();

// Step 2: Generate quiz from those notes
const quizResponse = await fetch('http://localhost:8000/quiz/generate-from-topic', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    topic: notes.topic,
    summary: notes.summary,
    key_points: notes.key_points,
    num_questions: 5
  })
});
const quiz = await quizResponse.json();

console.log('Study Notes:', notes);
console.log('Quiz Questions:', quiz.questions);
```

## Direct Usage (Backend Code)

```python
from agents.quiz_agent import (
    generate_quiz,
    generate_quiz_with_fallback,
    generate_quiz_from_topic
)

# Generate from raw notes
quiz = await generate_quiz(
    notes="Your study material...",
    num_questions=5,
    model="meta-llama/llama-3.1-8b-instruct:free"
)

# Generate with automatic fallback
quiz = await generate_quiz_with_fallback(
    notes="Your study material...",
    num_questions=5
)

# Generate from structured notes
quiz = await generate_quiz_from_topic(
    topic="Topic name",
    summary="Brief summary",
    key_points=["point 1", "point 2"],
    num_questions=5
)

# Access questions
for q in quiz:
    print(f"Q: {q['question']}")
    print(f"Options: {q['options']}")
    print(f"Answer: {q['answer']}")
    print(f"Explanation: {q['explanation']}")
```

## Validation & Quality Assurance

The quiz agent includes comprehensive validation:

### ✅ Question Uniqueness
- Removes duplicate questions
- Ensures diverse question coverage

### ✅ Format Validation
- Exactly 4 options per question
- Options properly labeled (A, B, C, D)
- Valid answer (must be A, B, C, or D)

### ✅ Quality Checks
- Questions must be clear and complete
- Each question has exactly one correct answer
- Explanations provided for learning

### ✅ Error Handling
- Validates input (notes not empty)
- Checks question count (1-20)
- Graceful fallback to alternative models
- Clear error messages

## Testing

```bash
cd backend
python test_quiz_agent.py
```

This will:
1. Test basic quiz generation from notes
2. Test structured notes → quiz conversion
3. Display all generated questions
4. Verify validation is working

## Models Used

Same as research agent:
- Primary: `meta-llama/llama-3.1-8b-instruct:free`
- Fallback 1: `mistralai/mixtral-8x7b-instruct:free`
- Fallback 2: `google/gemini-flash-1.5-8b`

All models are **FREE** on OpenRouter!

## Configuration

### Change Number of Questions

```python
# In the request
{
  "notes": "...",
  "num_questions": 10  # Generate 10 questions
}
```

### Adjust Creativity

Edit `backend/agents/quiz_agent.py`:

```python
payload = {
    "temperature": 0.9,  # Higher = more creative/diverse questions
    # ...
}
```

## Error Handling

Common errors:

### Empty Notes
```
Notes cannot be empty
```
**Solution:** Provide study material

### Invalid Question Count
```
Number of questions must be between 1 and 20
```
**Solution:** Use 1-20 for num_questions

### API Key Missing
```
OPENROUTER_API_KEY not found
```
**Solution:** Add API key to `.env`

### Not Enough Valid Questions
```
Only generated 3 valid questions, expected 5
```
**Solution:** Provide more comprehensive notes or reduce num_questions

## Tips for Best Results

1. **Provide Detailed Notes** - More content = better questions
2. **Use Key Points** - Structured notes work better
3. **Start Small** - Test with 3-5 questions first
4. **Review Questions** - AI-generated, may need human review
5. **Combine with Notes Agent** - Use research agent output directly
