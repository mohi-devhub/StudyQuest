# StudyQuest Backend - Quick Start Guide

## 🚀 Setup

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit `backend/.env`:
```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# OpenRouter Configuration (for AI features)
OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Application Configuration
ENVIRONMENT=development
```

**Get API Keys:**
- **Supabase**: https://supabase.com → Your Project → Settings → API
- **OpenRouter**: https://openrouter.ai/keys (FREE account)

### 3. Set Up Database

1. Go to Supabase Dashboard → SQL Editor
2. Run the SQL from `docs/supabase-setup.md`
3. Verify tables are created

### 4. Start the Server

```bash
cd backend
python main.py
```

Server runs at: http://localhost:8000

**API Documentation**: http://localhost:8000/docs

---

## 📚 Available Endpoints

### Authentication (`/auth`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/auth/signup` | POST | Register new user | No |
| `/auth/login` | POST | Login user (get JWT) | No |
| `/auth/user` | GET | Get current user | Yes |
| `/auth/logout` | POST | Logout user | Yes |

### Study Notes (`/study`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/study/generate-notes` | POST | Generate AI study notes from topic | Yes |

### Quiz (`/quiz`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/quiz/generate` | POST | Generate quiz from raw notes | Yes |
| `/quiz/generate-from-topic` | POST | Generate quiz from structured notes | Yes |

### Progress (`/progress`)

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/progress/` | GET | Get user progress (placeholder) | No |

---

## 🎯 Common Workflows

### 1. User Registration & Login

```bash
# Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"secure123"}'

# Response includes access_token
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {...}
}

# Use this token for authenticated requests
```

### 2. Generate Study Notes

```bash
TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/study/generate-notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python Functions"}'

# Response
{
  "topic": "Python Functions",
  "summary": "...",
  "key_points": ["...", "..."]
}
```

### 3. Generate Quiz from Notes

```bash
curl -X POST http://localhost:8000/quiz/generate-from-topic \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python Functions",
    "summary": "Functions are reusable code blocks...",
    "key_points": ["Uses def keyword", "Can return values"],
    "num_questions": 5
  }'

# Response
{
  "questions": [
    {
      "question": "What keyword defines a function?",
      "options": ["A) func", "B) def", "C) function", "D) define"],
      "answer": "B",
      "explanation": "..."
    }
  ],
  "total_questions": 5
}
```

### 4. Complete Flow (JavaScript Example)

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'student@example.com',
    password: 'secure123'
  })
});
const { access_token } = await loginResponse.json();

// 2. Generate Notes
const notesResponse = await fetch('http://localhost:8000/study/generate-notes', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ topic: 'React Hooks' })
});
const notes = await notesResponse.json();

// 3. Generate Quiz
const quizResponse = await fetch('http://localhost:8000/quiz/generate-from-topic', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
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

console.log('Notes:', notes);
console.log('Quiz:', quiz);
```

---

## 🧪 Testing

### Test Individual Agents

```bash
cd backend

# Test research agent (notes generator)
python test_research_agent.py

# Test quiz agent (question generator)
python test_quiz_agent.py

# Test complete workflow
python demo_workflow.py
```

### Test API with Swagger UI

1. Start server: `python main.py`
2. Visit: http://localhost:8000/docs
3. Click "Authorize" button
4. Login to get token
5. Paste token in authorization dialog
6. Try endpoints directly in browser

---

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (don't commit!)
├── .env.example           # Template for .env
│
├── config/
│   └── supabase_client.py # Supabase initialization
│
├── routes/
│   ├── auth.py            # Authentication endpoints
│   ├── study.py           # Study notes endpoints
│   ├── quiz.py            # Quiz generation endpoints
│   └── progress.py        # Progress tracking (placeholder)
│
├── agents/
│   ├── research_agent.py  # AI notes generator
│   └── quiz_agent.py      # AI quiz generator
│
└── utils/
    └── auth.py            # JWT verification & user dependencies
```

---

## 🔧 Configuration

### Change AI Models

Edit `backend/agents/research_agent.py` or `backend/agents/quiz_agent.py`:

```python
# Try different free models
models = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mixtral-8x7b-instruct:free",
    "google/gemini-flash-1.5-8b",
    # Add more from https://openrouter.ai/models
]
```

### Adjust CORS Origins

Edit `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-production-domain.com"
    ],
    # ...
)
```

### Change Server Port

```bash
# In main.py
uvicorn.run(app, host="0.0.0.0", port=8080)

# Or via command line
uvicorn main:app --port 8080
```

---

## 📖 Documentation

- **Authentication API**: `docs/auth-api.md`
- **Research Agent**: `docs/research-agent.md`
- **Quiz Agent**: `docs/quiz-agent.md`
- **Database Setup**: `docs/supabase-setup.md`
- **API Docs (Interactive)**: http://localhost:8000/docs

---

## ⚠️ Troubleshooting

### Import Errors
```bash
# Make sure you're in the backend directory
cd backend
python main.py
```

### API Key Not Found
```
OPENROUTER_API_KEY not found
```
**Solution**: Add key to `backend/.env` file

### Supabase Connection Failed
```
SUPABASE_URL and SUPABASE_KEY must be set
```
**Solution**: Add Supabase credentials to `.env`

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### CORS Errors (from frontend)
**Solution**: Add your frontend URL to CORS origins in `main.py`

---

## 🚀 Next Steps

1. ✅ Set up frontend (Next.js)
2. ✅ Implement progress tracking
3. ✅ Add study session management
4. ✅ Create user dashboard
5. ✅ Deploy to production

---

## 📝 Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | Yes | `https://xxx.supabase.co` |
| `SUPABASE_KEY` | Supabase anon/public key | Yes | `eyJhbGc...` |
| `OPENROUTER_API_KEY` | OpenRouter API key | Yes* | `sk-or-v1-...` |
| `ENVIRONMENT` | App environment | No | `development` or `production` |

*Required for AI features (notes & quiz generation)

---

## 💰 Cost

- **Supabase**: Free tier (500MB database, 50K monthly active users)
- **OpenRouter**: FREE models used by default
- **Hosting**: Free on Vercel/Railway/Render

**Total: $0/month** for development and small-scale usage!
