# StudyQuest

A terminal-style adaptive learning platform with real-time progress tracking and AI-powered quiz generation.

## ✨ Features

- 🖥️ **Terminal UI** - Monochrome dashboard with B/W design aesthetic
- 🎯 **Adaptive Quizzes** - Dynamic difficulty based on performance
- 🤖 **AI Coach** - Personalized feedback and topic recommendations
- ⚡ **Real-time Updates** - Live XP tracking and leaderboard
- 📊 **Progress Dashboard** - Detailed topic breakdown with retry functionality
- 🏆 **Competitive Leaderboard** - See how you rank globally
- 🎖️ **Badge System** - 21 badges across 4 tiers (Bronze to Platinum)
- 🔄 **Retry & Review** - Reinforce learning with topic retries (+10 XP)
- 📈 **XP Tracking** - Complete history with level progression (500 XP/level)
- 🎨 **Performance Optimized** - <1.2s page loads, 60fps animations

## 🏗️ Tech Stack

**Frontend:**
- Next.js 14 + TypeScript
- Tailwind CSS + Framer Motion
- Supabase Realtime
- JetBrains Mono (preloaded)

**Backend:**
- FastAPI + Python
- OpenRouter AI (Gemini 2.0 Flash)
- Supabase PostgreSQL

**Design:**
- Strict B/W monochrome palette
- Terminal-style animations
- Mobile responsive (375px - 1920px)

## 📁 Project Structure

```
StudyQuest/
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # Utilities (Supabase, caching)
├── backend/
│   ├── agents/           # AI agents
│   ├── routes/           # API endpoints
│   └── utils/            # Helper functions
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Supabase account
- OpenRouter API key

### Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Add your Supabase credentials to .env.local
npm run dev
# → http://localhost:3000
```

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
uvicorn main:app --reload
# → http://localhost:8000
```

### Database Setup

Run `SUPABASE_SCHEMA.sql` in your Supabase SQL Editor to create tables and enable real-time.

## 📚 Documentation

- **[Security Audit](SECURITY_AUDIT_REPORT.md)** - Security review and recommendations
- **[Project Status](PROJECT_STATUS.md)** - Complete feature overview
- **[Quiz System](QUIZ_GUIDE.md)** - Quiz flow and implementation
- **[Real-time Features](REALTIME_GUIDE.md)** - Live updates guide
- **[Badge System](MIGRATION_BADGES_MILESTONES.sql)** - Achievement schema and setup
- **[UI Optimization](UI_POLISH_COMPLETE.md)** - Performance details
- **[E2E Testing](E2E_TESTING_GUIDE.md)** - Testing procedures
- **[Design Checklist](VISUAL_DESIGN_CHECKLIST.md)** - B/W design validation

## 🎨 Design System

**Colors:**
```css
--bg: #000000      /* Black background */
--text: #FFFFFF    /* White text */
--border: #CCCCCC  /* Gray borders */
--muted: #808080   /* Muted text */
```

**Animations:**
- Hover: Scale (1.02x, 100ms)
- Page transitions: <200ms
- All effects: 60fps

## ⚡ Performance

- **Page Load:** 1.2s (52% faster)
- **Font Load:** 200ms (75% faster)
- **Cached API:** 5ms (160x faster)
- **Lighthouse:** 95/100

## 🧪 Testing

```bash
# Run E2E test suite
chmod +x test_e2e.sh
./test_e2e.sh

# Backend tests
cd backend
pytest tests/ -v
```

## 🚧 Status

**Recently Added (Nov 6, 2025):**
- ✅ Enhanced Progress Dashboard (progress_v2 API with 8 endpoints)
- ✅ Badge & Milestone System (21 badges, 13 milestones, auto-award)
- ✅ Adaptive Coach Feedback (AI-powered topic recommendations)
- ✅ Retry & Review Flow (topic reinforcement with XP rewards)

**Core Features:**
- ✅ Dashboard with XP tracking
- ✅ Quiz system (start to result)
- ✅ Real-time leaderboard
- ✅ AI coach feedback
- ✅ Mobile responsive
- ✅ Performance optimized

**API Endpoints:** 7 routers, 40+ endpoints
**Database Tables:** 10 tables (users, progress, xp_history, quiz_scores, user_topics, badges, user_badges, milestones, user_milestones, quiz_results)

**Ready for:**
- Production deployment (after security hardening)
- User authentication integration

## 📝 License

TBD
