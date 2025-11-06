# StudyQuest 🎓# StudyQuest



> **A monochrome terminal-style learning platform powered by AI**A terminal-style adaptive learning platform with real-time progress tracking and AI-powered quiz generation.



StudyQuest is a full-stack learning application that combines AI-generated study materials with gamified progress tracking. Built with Next.js, FastAPI, and Supabase, it features a unique black-and-white terminal aesthetic inspired by developer tools.## ✨ Features



![StudyQuest](https://img.shields.io/badge/version-1.0.0-black)- 🖥️ **Terminal UI** - Monochrome dashboard with B/W design aesthetic

![License](https://img.shields.io/badge/license-MIT-black)- 🎯 **Adaptive Quizzes** - Dynamic difficulty based on performance

![TypeScript](https://img.shields.io/badge/TypeScript-5.3-black)- 🤖 **AI Coach** - Personalized feedback and topic recommendations

![Python](https://img.shields.io/badge/Python-3.11-black)- ⚡ **Real-time Updates** - Live XP tracking and leaderboard

- 📊 **Progress Dashboard** - Detailed topic breakdown with retry functionality

---- 🏆 **Competitive Leaderboard** - See how you rank globally

- 🎖️ **Badge System** - 21 badges across 4 tiers (Bronze to Platinum)

## ✨ Features- 🔄 **Retry & Review** - Reinforce learning with topic retries (+10 XP)

- 📈 **XP Tracking** - Complete history with level progression (500 XP/level)

### 🤖 AI-Powered Learning- 🎨 **Performance Optimized** - <1.2s page loads, 60fps animations

- **Adaptive Study Notes**: Generate personalized study materials on any topic

- **Smart Quiz Generation**: AI creates quizzes tailored to your level## 🏗️ Tech Stack

- **Intelligent Feedback**: Real-time coaching and improvement suggestions

- **Topic Recommendations**: AI analyzes your performance and suggests next steps**Frontend:**

- Next.js 14 + TypeScript

### 🎮 Gamification System- Tailwind CSS + Framer Motion

- **XP & Levels**: Earn experience points for every study session and quiz- Supabase Realtime

- **Achievement Badges**: Unlock badges for milestones (First Steps, Quiz Master, etc.)- JetBrains Mono (preloaded)

- **Real-time Updates**: Live XP gains with celebration animations

- **Leaderboard**: Compete with other learners**Backend:**

- FastAPI + Python

### 🔒 Authentication & Security- OpenRouter AI (Gemini 2.0 Flash)

- **Supabase Auth**: Secure email/password authentication- Supabase PostgreSQL

- **Row Level Security (RLS)**: Database-level access control

- **JWT Tokens**: Stateless authentication**Design:**

- **Rate Limiting**: Prevents API abuse (10 req/min)- Strict B/W monochrome palette

- **CORS Protection**: Explicit origin whitelist- Terminal-style animations

- Mobile responsive (375px - 1920px)

### 📊 Progress Tracking

- **Topic Mastery**: Track progress across multiple topics## 📁 Project Structure

- **Performance Analytics**: View detailed statistics and trends

- **Study History**: Complete timeline of all activities```

- **Retry Mechanism**: Improve scores on previously attempted quizzesStudyQuest/

├── frontend/

---│   ├── app/              # Next.js pages

│   ├── components/       # React components

## 🛠️ Tech Stack│   └── lib/              # Utilities (Supabase, caching)

├── backend/

### Frontend│   ├── agents/           # AI agents

- **Framework**: Next.js 14 (React 18)│   ├── routes/           # API endpoints

- **Styling**: Tailwind CSS│   └── utils/            # Helper functions

- **Animations**: Framer Motion└── docs/                 # Documentation

- **Font**: JetBrains Mono (monospace)```

- **Auth**: Supabase SSR

- **State**: React Hooks + Context## 🚀 Quick Start



### Backend### Prerequisites

- **Framework**: FastAPI 0.104- Node.js 18+

- **AI**: LangChain + OpenRouter- Python 3.8+

- **Database**: Supabase (PostgreSQL)- Supabase account

- **Auth**: Supabase Auth + JWT- OpenRouter API key

- **Security**: slowapi (rate limiting)

- **Python**: 3.11+### Frontend Setup



### Database```bash

- **Platform**: Supabasecd frontend

- **Type**: PostgreSQLnpm install

- **Tables**: 11 (users, progress, xp_logs, quiz_results, badges, etc.)cp .env.local.example .env.local

- **Security**: Row Level Security (RLS) policies# Add your Supabase credentials to .env.local

- **Real-time**: Supabase real-time subscriptionsnpm run dev

# → http://localhost:3000

### AI Models (via OpenRouter)```

- Study notes generation

- Quiz creation### Backend Setup

- Feedback analysis

- Recommendations```bash

cd backend

---python3 -m venv venv

source venv/bin/activate

## 🚀 Quick Startpip install -r requirements.txt

cp .env.example .env

### Prerequisites# Add your API keys to .env

- Node.js 18+uvicorn main:app --reload

- Python 3.11+# → http://localhost:8000

- Supabase account```

- OpenRouter API key

### Database Setup

### 1. Clone Repository

```bashRun `SUPABASE_SCHEMA.sql` in your Supabase SQL Editor to create tables and enable real-time.

git clone <your-repo-url>

cd StudyQuest## 📚 Documentation

```

- **[Security Audit](SECURITY_AUDIT_REPORT.md)** - Security review and recommendations

### 2. Backend Setup- **[Project Status](PROJECT_STATUS.md)** - Complete feature overview

```bash- **[Quiz System](QUIZ_GUIDE.md)** - Quiz flow and implementation

cd backend- **[Real-time Features](REALTIME_GUIDE.md)** - Live updates guide

pip install -r requirements.txt- **[Badge System](MIGRATION_BADGES_MILESTONES.sql)** - Achievement schema and setup

- **[UI Optimization](UI_POLISH_COMPLETE.md)** - Performance details

# Create .env file- **[E2E Testing](E2E_TESTING_GUIDE.md)** - Testing procedures

cp .env.example .env- **[Design Checklist](VISUAL_DESIGN_CHECKLIST.md)** - B/W design validation

# Edit .env and add your keys

## 🎨 Design System

# Run server

uvicorn main:app --reload**Colors:**

``````css

--bg: #000000      /* Black background */

### 3. Frontend Setup--text: #FFFFFF    /* White text */

```bash--border: #CCCCCC  /* Gray borders */

cd frontend--muted: #808080   /* Muted text */

npm install```



# Create .env.local file**Animations:**

cp .env.local.example .env.local- Hover: Scale (1.02x, 100ms)

# Edit .env.local and add your keys- Page transitions: <200ms

- All effects: 60fps

# Run dev server

npm run dev## ⚡ Performance

```

- **Page Load:** 1.2s (52% faster)

### 4. Database Setup- **Font Load:** 200ms (75% faster)

- **Cached API:** 5ms (160x faster)

1. Create Supabase project at [supabase.com](https://supabase.com)- **Lighthouse:** 95/100

2. In Supabase SQL Editor, run:

   - `SUPABASE_SCHEMA.sql` (creates tables)## 🧪 Testing

   - `migrations/UPDATE_RLS_POLICIES_DEMO_MODE.sql` (dev RLS)

3. Create test user in Authentication → Users:```bash

   - Email: `test@studyquest.dev`# Run E2E test suite

   - Password: `testuser123`chmod +x test_e2e.sh

4. Run `migrations/CREATE_TEST_USER.sql`./test_e2e.sh



### 5. Access Application# Backend tests

cd backend

Open http://localhost:3000 and login with:pytest tests/ -v

- **Email**: `test@studyquest.dev````

- **Password**: `testuser123`

## 🚧 Status

---

**Recently Added (Nov 6, 2025):**

## 📖 Documentation- ✅ Enhanced Progress Dashboard (progress_v2 API with 8 endpoints)

- ✅ Badge & Milestone System (21 badges, 13 milestones, auto-award)

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Complete installation instructions- ✅ Adaptive Coach Feedback (AI-powered topic recommendations)

- **[Production Deployment](PRODUCTION_DEPLOYMENT_GUIDE.md)** - Deploy to production- ✅ Retry & Review Flow (topic reinforcement with XP rewards)

- **[API Reference](docs/BACKEND_API_COMPLETE.md)** - Backend API docs

- **[Security Audit](COMPREHENSIVE_SECURITY_AUDIT.md)** - Security overview**Core Features:**

- ✅ Dashboard with XP tracking

---- ✅ Quiz system (start to result)

- ✅ Real-time leaderboard

## 🔐 Security Features- ✅ AI coach feedback

- ✅ Mobile responsive

1. **Authentication**: JWT-based with Supabase Auth- ✅ Performance optimized

2. **Authorization**: Row Level Security (RLS) on all tables

3. **Rate Limiting**: 10 requests/minute per IP**API Endpoints:** 7 routers, 40+ endpoints

4. **CORS**: Explicit origin whitelist (no wildcards)**Database Tables:** 10 tables (users, progress, xp_history, quiz_scores, user_topics, badges, user_badges, milestones, user_milestones, quiz_results)

5. **Security Headers**: HSTS, X-Frame-Options, etc.

6. **Environment Variables**: No hardcoded secrets**Ready for:**

- Production deployment (after security hardening)

---- User authentication integration



## 📁 Project Structure## 📝 License



```TBD

StudyQuest/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── routes/              # API endpoints
│   ├── utils/               # Auth, DB helpers
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── login/           # Login page
│   │   ├── signup/          # Signup page
│   │   ├── page.tsx         # Dashboard
│   │   ├── study/           # Study notes
│   │   ├── quiz/            # Quizzes
│   │   ├── progress/        # Progress tracking
│   │   └── achievements/    # Badges
│   ├── components/          # React components
│   ├── lib/
│   │   ├── useAuth.tsx      # Auth context
│   │   └── supabase.ts      # Supabase client
│   └── middleware.ts        # Route protection
├── migrations/              # Database migrations
└── docs/                    # Documentation
```

---

## 🚢 Deployment

### Quick Deploy

**Backend** (Railway):
```bash
railway up
```

**Frontend** (Vercel):
```bash
vercel --prod
```

**Database** (Supabase):
- Run `migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql`
- Run `migrations/CLEANUP_DEMO_DATA.sql`

See [PRODUCTION_DEPLOYMENT_GUIDE.md](PRODUCTION_DEPLOYMENT_GUIDE.md) for details.

---

## 🎯 Key Features

### Authentication Flow
```
User → /login → Supabase Auth → JWT Token → Protected Routes
```

### XP System
- Study Session: +50 XP
- Easy Quiz: +100 XP (80%+ score)
- Medium Quiz: +150 XP (80%+ score)
- Hard Quiz: +200 XP (80%+ score)
- Level Up: Every 500 XP

### Data Flow
```
Frontend → Middleware (Auth) → Backend API → Supabase → Real-time Updates
```

---

## 🧪 Testing

### Manual Test Checklist
- [ ] Login with test user
- [ ] Sign up new user
- [ ] Generate study notes
- [ ] Take quiz and earn XP
- [ ] View progress page
- [ ] Check achievements
- [ ] View leaderboard
- [ ] Test logout/login flow

### Run Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
npm run build
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Credits

- Supabase - Database & Auth
- OpenRouter - AI Models
- FastAPI - Backend Framework
- Next.js - Frontend Framework
- Vercel - Frontend Hosting

---

## 📞 Support

- GitHub Issues
- Documentation in `/docs`
- Setup Guide: [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)

---

**Built with 🖤 in monochrome**

```bash
$ studyquest --start
> Loading knowledge...
> System ready.
> Begin your quest! 🚀
```
