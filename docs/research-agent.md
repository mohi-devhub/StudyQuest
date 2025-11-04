# Research Agent - Notes Generator

## Overview

The Research Agent uses OpenRouter API to generate AI-powered study notes from any topic. It leverages open-source LLMs like Meta's Llama or Mistral's Mixtral models.

## Setup

### 1. Get OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai/)
2. Sign up for a free account
3. Navigate to [API Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Copy the key to your `.env` file:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 2. Available Models

The agent uses free models by default:
- `meta-llama/llama-3.1-8b-instruct:free` (default)
- `mistralai/mixtral-8x7b-instruct:free` (fallback)
- `google/gemini-flash-1.5-8b` (second fallback)

## Usage

### API Endpoint

**POST** `/study/generate-notes`

**Headers:**
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

**Request:**
```json
{
  "topic": "Python Data Structures"
}
```

**Response:**
```json
{
  "topic": "Python Data Structures",
  "summary": "Python provides built-in data structures like lists, tuples, dictionaries, and sets to organize and store data efficiently.",
  "key_points": [
    "Lists are ordered, mutable collections that can hold items of different types",
    "Tuples are immutable sequences, useful for fixed collections of items",
    "Dictionaries store key-value pairs for fast lookups",
    "Sets are unordered collections of unique elements",
    "Each data structure has specific use cases and performance characteristics"
  ]
}
```

### Example with cURL

```bash
# Get your token first by logging in
TOKEN="your_jwt_token_here"

# Generate notes
curl -X POST http://localhost:8000/study/generate-notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Machine Learning Basics"}'
```

### Example with Python

```python
import httpx
import asyncio

async def generate_study_notes(topic: str, token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/study/generate-notes",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={"topic": topic}
        )
        return response.json()

# Usage
token = "your_jwt_token"
notes = asyncio.run(generate_study_notes("React Hooks", token))
print(notes)
```

### Example with JavaScript/Frontend

```javascript
async function generateNotes(topic) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/study/generate-notes', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ topic })
  });
  
  return response.json();
}

// Usage
const notes = await generateNotes('JavaScript Promises');
console.log(notes);
```

## Direct Usage (Backend Code)

```python
from agents.research_agent import generate_notes, generate_notes_with_fallback

# Generate notes with specific model
notes = await generate_notes(
    topic="Database Normalization",
    model="meta-llama/llama-3.1-8b-instruct:free"
)

# Generate notes with automatic fallback if primary model fails
notes = await generate_notes_with_fallback(
    topic="Database Normalization"
)

print(notes)
# {
#   "topic": "Database Normalization",
#   "summary": "...",
#   "key_points": [...]
# }
```

## Features

- ✅ **Free Models**: Uses free OpenRouter models (no cost)
- ✅ **Automatic Fallback**: Tries multiple models if one fails
- ✅ **JSON Response**: Structured output for easy parsing
- ✅ **Beginner-Friendly**: Optimized for learning (5-7 bullet points)
- ✅ **Async**: Non-blocking API calls
- ✅ **Error Handling**: Comprehensive error messages

## Error Handling

Common errors and solutions:

### 1. API Key Not Set
```
Server configuration error: OPENROUTER_API_KEY not found
```
**Solution**: Add your OpenRouter API key to `.env`

### 2. Rate Limiting
```
OpenRouter API error: 429 - Rate limit exceeded
```
**Solution**: Wait a moment and try again, or upgrade your OpenRouter plan

### 3. Model Unavailable
```
All models failed
```
**Solution**: The agent automatically tries multiple models, but if all fail, check OpenRouter status

## Customization

### Change Default Model

Edit `backend/agents/research_agent.py`:

```python
async def generate_notes(topic: str, model: str = "your-preferred-model") -> Dict:
    # ...
```

### Adjust Prompt

Modify the prompt in `research_agent.py` to change the output format or style:

```python
prompt = f"""Your custom prompt for {topic}..."""
```

### Change Temperature

Adjust creativity (0.0 = focused, 1.0 = creative):

```python
payload = {
    "temperature": 0.5,  # More focused responses
    # ...
}
```

## Cost

All default models are **FREE** on OpenRouter! No credit card required.

For higher limits or premium models, check [OpenRouter Pricing](https://openrouter.ai/docs#pricing).
