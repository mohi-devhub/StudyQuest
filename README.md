# StudyQuest

> A terminal-style adaptive learning platform with real-time progress tracking and AI-powered quiz generation.

![version](https://img.shields.io/badge/version-1.0.0-black) ![license](https://img.shields.io/badge/license-MIT-black) ![TypeScript](https://img.shields.io/badge/TypeScript-5.3-black) ![Python](https://img.shields.io/badge/Python-3.11-black)

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

## 📝 License

This project is licensed under the **Apache 2.0 License** - see the [LICENSE](LICENSE) file for details.


