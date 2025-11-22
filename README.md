# StudyQuest

> A terminal-style adaptive learning platform with real-time progress tracking and AI-powered quiz generation.

![version](https://img.shields.io/badge/version-1.0.0-black) ![license](https://img.shields.io/badge/license-MIT-black) ![TypeScript](https://img.shields.io/badge/TypeScript-5.3-black) ![Python](https://img.shields.io/badge/Python-3.11-black)

[![Test Suite](https://github.com/YOUR_USERNAME/studyquest/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/studyquest/actions/workflows/test.yml)
[![Deploy to Production](https://github.com/YOUR_USERNAME/studyquest/actions/workflows/deploy.yml/badge.svg)](https://github.com/YOUR_USERNAME/studyquest/actions/workflows/deploy.yml)
[![Security Scan](https://github.com/YOUR_USERNAME/studyquest/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_USERNAME/studyquest/actions/workflows/security.yml)

StudyQuest is a full-stack learning application built with Next.js, FastAPI, and Supabase, featuring a unique monochrome terminal aesthetic.

---

## Key Features

* **AI-Powered Learning**: Generates adaptive study notes and quizzes on any topic.
* **AI Coach**: Provides personalized feedback and topic recommendations.
* **Gamification**: Includes XP/level tracking, badges, and a real-time leaderboard.
* **Progress Tracking**: Features a detailed dashboard with topic mastery and study history.
* **Monochrome UI**: A performance-optimized terminal-style interface.
* **Secure Auth**: Built with Supabase Auth, JWTs, and Row Level Security (RLS).

---

## Tech Stack

* **Frontend**: Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion
* **Backend**: FastAPI, Python 3.11+, LangChain, OpenRouter
* **Database**: Supabase (PostgreSQL), Supabase Realtime
* **Authentication**: Supabase Auth (SSR & JWT)

---

## 🚀 Quick Start

### Prerequisites

* Node.js 18+
* Python 3.11+
* Supabase Account
* OpenRouter API Key

### 1. Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add API keys to .env
uvicorn main:app --reload
# → Backend running at http://localhost:8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
cp .env.local.example .env.local
# Add Supabase credentials to .env.local
npm run dev
# → Frontend running at http://localhost:3000
```

### 3. Database Setup
1. Create a new project on supabase.com.

2. In the Supabase SQL Editor, run the contents of SUPABASE_SCHEMA.sql.

3. Run the contents of migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql.

4. Run migrations/CREATE_TEST_USER.sql to create a test user.
   

### 4. Access Application
Open http://localhost:3000 and log in:

- Email: test@studyquest.dev

- Password: testuser123


---

## 🐳 Docker Deployment

StudyQuest can be deployed using Docker for both local development and production environments.

### Quick Start with Docker

```bash
# 1. Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# Edit both files with your actual values

# 2. Start all services
docker-compose up -d

# 3. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Docker Features

- **Multi-stage builds**: Optimized image sizes (Backend: ~200MB, Frontend: ~150MB)
- **Non-root users**: Enhanced security with dedicated service users
- **Health checks**: Automatic monitoring of service health
- **Resource limits**: CPU and memory constraints for stability
- **Auto-restart**: Automatic recovery from failures

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

For detailed Docker deployment instructions, see [Docker Deployment Guide](docs/deployment/DOCKER_DEPLOYMENT.md).

---

## 🔄 CI/CD Pipeline

StudyQuest uses GitHub Actions for automated testing and deployment.

### Workflows

1. **Test Suite** - Runs on every push and PR
   - Backend: pytest, coverage, pip-audit
   - Frontend: ESLint, TypeScript, Jest, npm audit
   
2. **Deploy to Production** - Runs on pushes to `main`
   - Automated deployment to Render (backend) and Vercel (frontend)
   - Health checks and rollback on failure
   
3. **Security Scan** - Runs weekly and on PRs
   - Dependency vulnerability scanning
   - Secret detection
   - Code security analysis

### Deployment Process

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and push
git push origin feature/my-feature

# 3. Create PR (tests run automatically)

# 4. Merge to main (deploys automatically)
```

For detailed CI/CD setup and configuration, see [CI/CD Guide](docs/deployment/CICD_GUIDE.md).

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Pages      │  │  Components  │  │   Hooks      │      │
│  │  - Study     │  │  - TopicCard │  │  - useAuth   │      │
│  │  - Quiz      │  │  - XPBar     │  │  - useXP     │      │
│  │  - Progress  │  │  - Coach     │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Structured Logging (JSON)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS/REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Routes     │  │    Agents    │  │   Utils      │      │
│  │  - Study     │  │  - Quiz Gen  │  │  - Auth      │      │
│  │  - Progress  │  │  - Coach     │  │  - Cache     │      │
│  │  - Health    │  │  - Research  │  │  - Logger    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Middleware: Auth, Rate Limiting, CORS, Validation   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Structured Logging (JSON)                     │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────┬───────────────────────┘
             │                        │
             ▼                        ▼
┌─────────────────────┐  ┌─────────────────────────────────┐
│  Supabase (DB)      │  │  OpenRouter (AI)                │
│  - PostgreSQL       │  │  - Quiz Generation              │
│  - Auth             │  │  - Recommendations              │
│  - Realtime         │  │  - Coaching                     │
│  - RLS              │  │  - Response Caching             │
└─────────────────────┘  └─────────────────────────────────┘
```

### Key Components

**Frontend:**
- Next.js 14 with App Router
- Server-side rendering (SSR) for auth
- Real-time XP updates via Supabase Realtime
- Structured JSON logging

**Backend:**
- FastAPI with async/await
- JWT authentication middleware
- Rate limiting (SlowAPI)
- AI response caching
- Connection pooling
- Structured JSON logging

**Database:**
- PostgreSQL via Supabase
- Row Level Security (RLS)
- Indexed queries for performance
- Real-time subscriptions

**AI System:**
- OpenRouter API integration
- Model: google/gemini-2.0-flash-exp:free
- Response caching (1-hour TTL)
- Fallback models configured

---

## 🏥 Health Checks

Monitor application health using built-in endpoints:

### Backend Health Endpoints

**Basic Health Check:**
```bash
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-22T10:30:00.000Z"
# }
```

**Detailed Health Check:**
```bash
curl http://localhost:8000/health/detailed

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-22T10:30:00.000Z",
#   "dependencies": {
#     "supabase": {
#       "status": "healthy",
#       "response_time_ms": 45
#     },
#     "openrouter": {
#       "status": "healthy"
#     }
#   }
# }
```

**Frontend Health Check:**
```bash
curl http://localhost:3000/api/health

# Response:
# {
#   "status": "healthy",
#   "backend": "connected",
#   "supabase": "connected"
# }
```

### Health Check Features

- **Automatic monitoring**: Docker health checks run every 30 seconds
- **Dependency validation**: Verifies Supabase and OpenRouter connectivity
- **Response time tracking**: Measures database query performance
- **Graceful degradation**: Reports "degraded" status if dependencies fail

---

## 🔧 Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000

# Verify environment variables
cat backend/.env

# Check Python version
python --version  # Should be 3.11+

# Reinstall dependencies
cd backend
pip install -r requirements.txt
```

#### Frontend Won't Start

```bash
# Check if port 3000 is in use
lsof -i :3000

# Verify environment variables
cat frontend/.env.local

# Clear Next.js cache
cd frontend
rm -rf .next
npm run build
npm run dev
```

#### Database Connection Errors

```bash
# Verify Supabase credentials
# Check SUPABASE_URL and SUPABASE_KEY in .env files

# Test connection
curl -X GET "https://YOUR_PROJECT.supabase.co/rest/v1/users?select=user_id&limit=1" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

#### CORS Errors

```bash
# Update ALLOWED_ORIGINS in backend/.env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Restart backend
cd backend
uvicorn main:app --reload
```

#### Docker Issues

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Clean slate
docker-compose down -v
docker-compose up -d --build
```

### Getting Help

1. Check health endpoints: `/health` and `/health/detailed`
2. Review logs: `docker-compose logs` or application logs
3. Consult documentation in `docs/` directory
4. Check [Operations Runbook](docs/deployment/OPERATIONS_RUNBOOK.md)
5. Open an issue on GitHub

---

## 📚 Documentation

- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup instructions
- [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md) - Container deployment guide
- [CI/CD Guide](docs/deployment/CICD_GUIDE.md) - Automated deployment setup
- [Operations Runbook](docs/deployment/OPERATIONS_RUNBOOK.md) - Monitoring and maintenance
- [Production Deployment](docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md) - Production setup
- [API Documentation](docs/BACKEND_API_COMPLETE.md) - Complete API reference
- [Database Schema](docs/database/SUPABASE_SCHEMA.sql) - Database structure
- [Security Audit](docs/security/COMPREHENSIVE_SECURITY_AUDIT.md) - Security review

---

## 🔒 Security

StudyQuest implements multiple security layers:

- **Authentication**: JWT-based auth with Supabase
- **Authorization**: Row Level Security (RLS) in database
- **Rate Limiting**: API endpoint protection (5-10 req/min)
- **Input Validation**: Request validation middleware
- **CORS**: Explicit origin whitelisting
- **Security Headers**: CSP, HSTS, X-Frame-Options
- **Dependency Scanning**: Automated vulnerability checks
- **Secret Scanning**: Prevents credential leaks
- **Non-root Containers**: Docker security best practices

For security reports, see [Security Documentation](docs/security/).

---

## 📝 License

This project is licensed under the **Apache 2.0 License** - see the [LICENSE](LICENSE) file for details.


