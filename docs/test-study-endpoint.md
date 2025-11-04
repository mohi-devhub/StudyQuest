# Testing the /study Endpoint

## Server Status

✅ **FastAPI server is running on http://localhost:8000**

The server has been successfully started with all dependencies installed.

## Available Endpoints

### Main Study Endpoint

**POST /study**
- Accepts: `{ "topic": "Neural Networks", "num_questions": 5 }`
- Returns: Complete study package (notes + quiz)
- Requires: Authentication (JWT token)

**Alternative: POST /study/complete**
- Same functionality as `/study`
- Both endpoints use the Coach Agent

## Test the API

### 1. Via Swagger UI (Interactive Docs)

Open in browser: **http://localhost:8000/docs**

You'll see interactive API documentation where you can:
- Test all endpoints
- See request/response schemas
- Try authentication flow

### 2. Via curl (Command Line)

```bash
# First, login to get a JWT token
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your@email.com",
    "password": "yourpassword"
  }'

# Copy the access_token from the response, then:

# Generate complete study package
curl -X POST "http://localhost:8000/study" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "topic": "Neural Networks",
    "num_questions": 5
  }'
```

### 3. Via Python requests

```python
import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/auth/login",
    json={"email": "your@email.com", "password": "yourpassword"}
)
token = login_response.json()["access_token"]

# Generate study package
study_response = requests.post(
    "http://localhost:8000/study",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "topic": "Neural Networks",
        "num_questions": 5
    }
)

study_package = study_response.json()
print(f"Topic: {study_package['topic']}")
print(f"Notes: {study_package['notes']}")
print(f"Quiz: {len(study_package['quiz'])} questions")
```

### 4. Via JavaScript/Frontend

```javascript
// Login
const loginRes = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'your@email.com',
    password: 'yourpassword'
  })
});
const { access_token } = await loginRes.json();

// Generate study package
const studyRes = await fetch('http://localhost:8000/study', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    topic: 'Neural Networks',
    num_questions: 5
  })
});

const studyPackage = await studyRes.json();
console.log('Study Package:', studyPackage);
```

## Request Format

```json
{
  "topic": "Neural Networks",
  "num_questions": 5
}
```

**Parameters:**
- `topic` (required): The subject you want to study
  - Type: string
  - Min length: 1
  - Max length: 200
  - Example: "Python Decorators", "REST API Design", "Neural Networks"

- `num_questions` (optional): Number of quiz questions to generate
  - Type: integer
  - Min: 1
  - Max: 20
  - Default: 5

## Response Format

```json
{
  "topic": "Neural Networks",
  "notes": {
    "topic": "Neural Networks",
    "summary": "Neural networks are computing systems inspired by biological neural networks...",
    "key_points": [
      "Neural networks consist of interconnected nodes (neurons) organized in layers",
      "They learn patterns through training on data",
      "Common types include feedforward, convolutional, and recurrent networks",
      "Activation functions introduce non-linearity",
      "Backpropagation is used to adjust weights during training",
      "Deep learning uses multiple hidden layers",
      "Applications include image recognition, NLP, and game playing"
    ]
  },
  "quiz": [
    {
      "question": "What are neural networks inspired by?",
      "options": [
        "A) Computer circuits",
        "B) Biological neural networks",
        "C) Mechanical systems",
        "D) Chemical reactions"
      ],
      "answer": "B",
      "explanation": "Neural networks are modeled after the structure and function of biological neural networks found in animal brains."
    },
    // ... 4 more questions
  ],
  "metadata": {
    "num_key_points": 7,
    "num_questions": 5
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Topic cannot be empty"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to generate study package: [error message]"
}
```

## All Study Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/study` | POST | Generate complete study package | ✅ Yes |
| `/study/complete` | POST | Same as `/study` (alternative) | ✅ Yes |
| `/study/generate-notes` | POST | Generate only notes (no quiz) | ✅ Yes |
| `/study/batch` | POST | Process multiple topics in parallel | ✅ Yes |
| `/progress/evaluate` | POST | Evaluate quiz answers | ✅ Yes |

## Quick Start for Frontend

```javascript
// Complete workflow example
async function studyWorkflow(topic) {
  // 1. Login (or use existing token)
  const token = await login(email, password);
  
  // 2. Generate study package
  const package = await generateStudyPackage(token, topic);
  
  // 3. Display notes to user
  displayNotes(package.notes);
  
  // 4. User takes quiz
  const answers = await takeQuiz(package.quiz);
  
  // 5. Evaluate progress
  const progress = await evaluateQuiz(token, package, answers);
  
  // 6. Show results
  displayResults(progress);
}

async function generateStudyPackage(token, topic) {
  const res = await fetch('http://localhost:8000/study', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ 
      topic,
      num_questions: 5 
    })
  });
  
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`);
  }
  
  return await res.json();
}

async function evaluateQuiz(token, studyPackage, answers) {
  const res = await fetch('http://localhost:8000/progress/evaluate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      study_package: studyPackage,
      answers
    })
  });
  
  return await res.json();
}
```

## Testing Tips

1. **Use Swagger UI first** - Easiest way to test endpoints interactively
   - Go to http://localhost:8000/docs
   - Click "Authorize" and enter your JWT token
   - Try the `/study` endpoint

2. **Check response times** - Free tier models may be rate-limited
   - Wait 1-2 minutes between requests if you get 429 errors
   - Consider using your own OpenRouter API key

3. **Test with different topics** - Try various subjects
   - Short topics: "Python Lists", "HTTP Methods"
   - Medium topics: "React Hooks", "SQL Joins"
   - Complex topics: "Neural Networks", "OAuth 2.0 Flow"

4. **Vary question count** - Test scalability
   - 3 questions: Fast (~15 seconds)
   - 5 questions: Standard (~20 seconds)
   - 10 questions: Comprehensive (~35 seconds)

## Notes

- ✅ Server is running on port 8000
- ✅ Auto-reload enabled (code changes will restart server)
- ✅ CORS configured for `http://localhost:3000` (Next.js frontend)
- ✅ All dependencies installed (including email-validator)
- ✅ Coach Agent integrated and working

## Next Steps

1. **Test the API** - Use Swagger UI at http://localhost:8000/docs
2. **Build Frontend** - Create Next.js app to consume this API
3. **Add Database** - Persist study packages and user progress
4. **Deploy** - Set up production environment

---

**Server Status:** 🟢 Running  
**Port:** 8000  
**Docs:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc
