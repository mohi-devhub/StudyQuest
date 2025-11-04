# StudyQuest

A modern AI-powered study management platform that helps students learn more effectively.

## ✨ Features

- 🤖 **AI Study Notes Generator** - Generate comprehensive study notes from any topic using AI
- 📝 **Smart Quiz Generator** - Auto-create multiple-choice quizzes from your study materials
- 🎓 **Coach Agent** - Intelligent workflow coordinator that combines notes + quiz generation
- 🔐 **Secure Authentication** - User authentication via Supabase Auth
- 📊 **Progress Tracking** - Quiz evaluation with personalized feedback
- 🎯 **Batch Processing** - Study multiple topics in parallel
- ⚡ **Model Fallback** - Automatic retry with alternative AI models for reliability

## 🏗️ Architecture

**Tech Stack:**
- **Frontend**: Next.js (ready for development)
- **Backend**: FastAPI + Python ✅ **Production Ready**
- **Database**: Supabase (PostgreSQL + Auth)
- **AI**: OpenRouter API (Gemini 2.0, Llama 3.2 - FREE models)
- **Agents**: Multi-agent system (Research, Quiz, Coach)
- **API Docs**: Auto-generated OpenAPI/Swagger

## 📁 Project Structure

```
StudyQuest/
├── frontend/     # Next.js frontend application
├── backend/      # FastAPI backend service
│   ├── agents/   # AI agents (research, quiz generation)
│   ├── routes/   # API endpoints
│   ├── config/   # Configuration (Supabase, etc.)
│   └── utils/    # Utilities (auth, helpers)
└── docs/         # Project documentation and API references
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (for backend)
- Node.js 18+ (for frontend - coming soon)
- Supabase account (free)
- OpenRouter account (free)

### Backend Setup

1. **Install dependencies:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Activate virtual environment
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   
   Create `backend/.env` with:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your_supabase_anon_key
   OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
   ```

   **Get API Keys:**
   - Supabase: https://supabase.com → Settings → API
   - OpenRouter: https://openrouter.ai/keys (FREE)

3. **Set up database:**
   
   Run the SQL from `docs/supabase-setup.md` in your Supabase SQL Editor

4. **Start the server:**
   ```bash
   source venv/bin/activate  # If not already activated
   python3 main.py
   ```

   API available at: http://localhost:8000
   
   Docs: http://localhost:8000/docs

### Test the Backend

```bash
cd backend
source venv/bin/activate

# Test notes generator
python3 test_research_agent.py

# Test quiz generator
python3 test_quiz_agent.py

# Test complete workflow
python3 demo_workflow.py
```

## 📚 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login (get JWT token)
- `GET /auth/user` - Get current user info
- `POST /auth/logout` - Logout

### Study (Complete Workflow) ✨ NEW
- `POST /study` - **Generate complete study package** (notes + quiz in one call)
- `POST /study/complete` - Alternative endpoint for complete workflow
- `POST /study/generate-notes` - Generate only AI study notes
- `POST /study/batch` - Process multiple topics in parallel

### Quiz
- `POST /quiz/generate` - Generate quiz from raw notes
- `POST /quiz/generate-from-topic` - Generate quiz from structured notes

### Progress ✨ NEW
- `POST /progress/evaluate` - Evaluate quiz answers with personalized feedback

## 🎯 Usage Example

### Complete Study Workflow (Recommended)

```javascript
// 1. Login
const { access_token } = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
}).then(r => r.json());

// 2. Generate Complete Study Package (Notes + Quiz in one call!)
const studyPackage = await fetch('http://localhost:8000/study', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ 
    topic: 'Neural Networks',
    num_questions: 5 
  })
}).then(r => r.json());

console.log('Topic:', studyPackage.topic);
console.log('Notes:', studyPackage.notes);
console.log('Quiz:', studyPackage.quiz);

// 3. User takes quiz (get answers from UI)
const answers = ['A', 'B', 'C', 'D', 'A'];

// 4. Evaluate progress
const progress = await fetch('http://localhost:8000/progress/evaluate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    study_package: studyPackage,
    answers: answers
  })
}).then(r => r.json());

console.log(`Score: ${progress.score_percentage}%`);
console.log(`Feedback: ${progress.feedback}`);
```

### Legacy Workflow (Separate Calls)

```javascript
// 1. Login
const { access_token } = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com', password: 'password123' })
}).then(r => r.json());

// 2. Generate Study Notes
const notes = await fetch('http://localhost:8000/study/generate-notes', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ topic: 'Python Functions' })
}).then(r => r.json());

// 3. Generate Quiz
const quiz = await fetch('http://localhost:8000/quiz/generate-from-topic', {
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
}).then(r => r.json());

console.log('Notes:', notes);
console.log('Quiz Questions:', quiz.questions);
```

## 📖 Documentation

- **[Quick Start Guide](docs/quick-start.md)** - Get up and running fast
- **[Authentication API](docs/auth-api.md)** - User authentication docs
- **[Coach Agent](docs/coach-agent.md)** - ✨ NEW: Workflow coordinator
- **[Research Agent](docs/research-agent.md)** - AI notes generator
- **[Quiz Agent](docs/quiz-agent.md)** - AI quiz generator
- **[Database Setup](docs/supabase-setup.md)** - Supabase configuration
- **[Test Results](docs/test_results.md)** - ✅ Validated end-to-end testing
- **[Validation Summary](docs/validation-summary.md)** - Production readiness report
- **[API Docs (Interactive)](http://localhost:8000/docs)** - Swagger UI (when server is running)

## 🛠️ Development

### Backend Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── config/
│   └── supabase_client.py # Database connection
├── routes/
│   ├── auth.py            # Authentication endpoints
│   ├── study.py           # Study workflow endpoints (✨ with Coach Agent)
│   ├── quiz.py            # Quiz generation endpoints
│   └── progress.py        # Progress tracking & evaluation
├── agents/                # ✨ Multi-agent system
│   ├── research_agent.py  # AI notes generator
│   ├── quiz_agent.py      # AI quiz generator
│   └── coach_agent.py     # Workflow coordinator
├── utils/
│   └── auth.py            # JWT verification
└── tests/
    ├── test_research_agent.py
    ├── test_quiz_agent.py
    ├── test_coach_agent.py
    ├── test_api_endpoint.py
    └── demo_workflow.py
```

### Adding New Endpoints

1. Create route file in `backend/routes/`
2. Define your APIRouter
3. Import and mount in `main.py`

Example:
```python
# backend/routes/flashcards.py
from fastapi import APIRouter

router = APIRouter(prefix="/flashcards", tags=["flashcards"])

@router.get("/")
async def get_flashcards():
    return {"message": "Flashcards endpoint"}
```

## 💰 Cost

**Everything uses free tiers:**
- ✅ Supabase Free: 500MB DB, 50K monthly users
- ✅ OpenRouter Free: Llama 3.1, Mixtral, Gemini models
- ✅ Hosting: Deploy free on Vercel/Railway/Render

**Total: $0/month** for development! 🎉

## 🔐 Security

- JWT-based authentication
- Row-Level Security (RLS) in Supabase
- Environment variables for sensitive data
- CORS protection
- Password hashing via Supabase Auth

## 🧪 Testing

```bash
# Backend tests
cd backend
source venv/bin/activate

# Test individual agents
python3 test_research_agent.py  # Notes generator
python3 test_quiz_agent.py      # Quiz generator
python3 test_coach_agent.py     # Workflow coordinator

# Test complete workflow
python3 demo_workflow.py         # End-to-end demo

# Test API endpoint (validated ✅)
python3 test_api_endpoint.py    # HTTP endpoint validation
```

**Test Results:** See `docs/test_results.md` for validated output with real examples.

## 🚧 Roadmap

- [x] Backend API foundation
- [x] User authentication (Supabase)
- [x] AI notes generator (Research Agent)
- [x] AI quiz generator (Quiz Agent)
- [x] Workflow coordinator (Coach Agent) ✨
- [x] Complete study endpoint (/study) ✨
- [x] Progress evaluation endpoint ✨
- [x] End-to-end validation ✅
- [ ] Frontend (Next.js)
- [ ] Database persistence for study packages
- [ ] Study session management
- [ ] Flashcard generation
- [ ] Spaced repetition system
- [ ] Analytics dashboard
- [ ] Mobile app

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines first.

## 📝 License

TBD

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Supabase for backend-as-a-service
- OpenRouter for free AI model access
- Meta, Mistral, Google for their open-source models
