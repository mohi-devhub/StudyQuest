
# StudyQuest: Official Developer Guide & Whitepaper

**Version:** 1.0.0  
**Last Updated:** November 7, 2025

---

## 1. Project Overview

### 1.1. Mission & Vision

StudyQuest is an AI-powered, gamified learning platform designed to make education engaging, measurable, and personalized. Our mission is to transform studying from a passive chore into an active quest for knowledge. By integrating game mechanics like Experience Points (XP), levels, quests, and streaks, we motivate learners to stay consistent and celebrate their progress.

The core idea is to provide a continuous, adaptive learning journey where users can tackle any topic, receive AI-generated study materials, test their knowledge with dynamic quizzes, and get personalized feedback to guide their growth.

### 1.2. Developer-Centric Aesthetic

The user interface is intentionally designed with a minimalist, developer-centric aesthetic:
- **Theme:** A pure black and white, terminal-style UI that feels familiar and focused.
- **Typography:** All text is rendered in **JetBrains Mono**, a popular coding font, for a clean, monospaced look.
- **Animations:** UI elements feature subtle, fast animations that mimic terminal output and command-line interactions.

This design choice creates a distraction-free environment that appeals to developers, tech enthusiasts, and anyone who appreciates a clean, functional interface.

---

## 2. System Architecture

### 2.1. High-Level Architecture

StudyQuest is a full-stack application composed of three main components: a Next.js frontend, a Python (FastAPI) backend, and a Supabase database. AI capabilities are integrated via the OpenRouter API.

```
+----------------------+      +----------------------+      +---------------------+
|                      |      |                      |      |                     |
|   Next.js Frontend   |----->|    FastAPI Backend   |----->|   OpenRouter API    |
| (Vercel)             |      | (Railway/Render)     |      | (AI Models)         |
|                      |      |                      |      |                     |
+----------------------+      +----------+-----------+      +---------------------+
       ^                                 |
       |                                 |
       | (Real-time Updates)             | (Data Storage & Auth)
       |                                 v
+------|---------------------------------+-----------------------+
|                                                                |
|                      Supabase (Backend-as-a-Service)             |
|                                                                |
|   +-----------------+  +------------------+  +-----------------+   |
|   |  PostgreSQL DB  |  |  Realtime API    |  |   Auth Service  |   |
|   +-----------------+  +------------------+  +-----------------+   |
|                                                                |
+----------------------------------------------------------------+
```

### 2.2. Component Interaction

1.  **Frontend (Next.js):** The user-facing application, built with Next.js and React. It handles UI rendering, user interactions, and communicates with both the FastAPI backend for business logic and Supabase for real-time data and authentication.
2.  **Backend (FastAPI):** A Python-based API server that orchestrates AI-powered features. It receives requests from the frontend, calls the OpenRouter API to generate content (study notes, quizzes, feedback), and processes complex business logic that is too intensive for the frontend.
3.  **Database (Supabase):** A PostgreSQL database that serves as the single source of truth. It stores all user data, progress, XP logs, and achievements.
    - **Supabase Auth:** Manages user authentication (signup, login, sessions) using JWTs.
    - **Supabase Realtime:** Pushes live data changes to the frontend (e.g., XP updates, leaderboard rankings) via websockets.
4.  **AI (OpenRouter):** A third-party service that provides access to various large language models (LLMs) like GPT, Gemini, and Claude. StudyQuest uses it for all AI-driven content generation.

### 2.3. Authentication Flow

Authentication is handled by Supabase Auth, providing a secure and scalable solution.

1.  User signs up or logs in via the Next.js frontend.
2.  Supabase Auth verifies the credentials and returns a JSON Web Token (JWT).
3.  The JWT is stored securely in the browser.
4.  For requests to protected frontend routes, Next.js middleware validates the JWT.
5.  For requests to the FastAPI backend, the JWT is passed in the `Authorization` header. The backend verifies the token using the shared JWT secret from Supabase.

### 2.4. Folder Structure

The project is organized into a monorepo-like structure with distinct `frontend` and `backend` directories.

```
StudyQuest/
├── frontend/
│   ├── app/                # Next.js App Router pages (e.g., /dashboard, /quiz)
│   ├── components/         # Reusable React components (e.g., XPProgressBar, Header)
│   ├── lib/                # Helper functions and hooks (e.g., Supabase client, auth)
│   ├── package.json        # Frontend dependencies
│   └── next.config.js      # Next.js configuration
├── backend/
│   ├── main.py             # FastAPI application entry point
│   ├── agents/             # AI agent logic (e.g., quiz generation, coaching)
│   ├── routes/             # API endpoint definitions
│   ├── utils/              # Utility functions (e.g., auth, error handling)
│   └── requirements.txt    # Backend dependencies
├── migrations/             # SQL migration scripts for the Supabase database
├── docs/                   # Project documentation
└── SUPABASE_SCHEMA.sql     # The complete database schema
```

---

## 3. Tech Stack

-   **Frontend:**
    -   Framework: **Next.js 14** (React 18)
    -   Language: **TypeScript**
    -   Styling: **TailwindCSS** with a custom monochrome theme
    -   UI Components: **ShadCN UI** (adapted for the terminal theme)
    -   Animations: **Framer Motion**
-   **Backend:**
    -   Database: **Supabase** (PostgreSQL)
    -   Real-time: **Supabase Realtime**
    -   Authentication: **Supabase Auth**
    -   Optional API Routes: Python **FastAPI** for AI logic
-   **AI:**
    -   Provider: **OpenRouter API**
    -   Models: Configurable, with defaults like **Google Gemini Pro** and **ChatGPT**.
-   **Deployment & Tools:**
    -   Frontend Hosting: **Vercel**
    -   Backend Hosting: **Railway** or **Render**
    -   Code Verification & Audit: **Gemini CLI**

---

## 4. Implementation Details

### 4.1. Authentication and User Sessions

-   **Files:** `frontend/lib/supabase.ts`, `frontend/lib/useAuth.tsx`, `frontend/middleware.ts`, `backend/utils/auth.py`
-   **Logic:** Supabase's `ssr` package is used for server-side authentication in Next.js. The `middleware.ts` file protects routes, redirecting unauthenticated users to the `/login` page. The `useAuth` hook provides user session data to frontend components. The backend verifies JWTs using a shared secret.

### 4.2. Dashboard and XP Tracking

-   **Files:** `frontend/app/page.tsx` (Dashboard), `frontend/components/XPProgressBar.tsx`
-   **Logic:** The main dashboard page fetches user progress and displays it. The `XPProgressBar` component visualizes the user's current XP and level. Real-time XP updates are received via a Supabase Realtime subscription, which triggers a re-render and a celebration animation.
-   **XP System:**
    -   **Level Up:** Every 500 XP.
    -   **XP Sources:** Completing quizzes, daily streaks, unlocking achievements, retrying topics.

### 4.3. Quest and Streak System

-   **Files:** `backend/routes/progress_v2.py`, `MIGRATION_BADGES_MILESTONES.sql`
-   **Logic:** The "Quest" system is implemented as a series of "Milestones" and "Badges." A PostgreSQL trigger (`on_user_xp_update`) automatically calls a function (`check_and_award_badges`) whenever a user's XP or level changes. This function checks if the user has met the criteria for any new badges or milestones.
-   **Example Badge:** "Curious Mind" - Unlocked at Level 10.

### 4.4. Study Logs and Progress Tracking

-   **Files:** `frontend/app/progress/page.tsx`, `backend/routes/progress_v2.py`, `SUPABASE_SCHEMA.sql`
-   **Logic:** All study activities are logged in the database.
    -   `user_topics`: Tracks performance on a per-topic basis (average score, attempts).
    -   `quiz_scores`: Stores the result of every quiz attempt.
    -   `xp_history`: A complete log of every XP point earned.
    -   The `/progress` page displays this data in a terminal-style table.

### 4.5. UI Theming and Design Principles

-   **Files:** `frontend/app/globals.css`, `frontend/tailwind.config.js`
-   **Logic:** The entire UI is themed using CSS variables defined in `globals.css`. This allows for a consistent black and white theme. TailwindCSS is configured to use these variables. All components are built with this strict color palette.

```css
/* frontend/app/globals.css */
:root {
  --bg: #000000;
  --text: #FFFFFF;
  --border: #CCCCCC;
  --muted: #808080;
}
```

### 4.6. AI Feature Integration

-   **Files:** `backend/agents/`
-   **Logic:** AI logic is encapsulated in "agents" in the backend.
    -   `adaptive_quiz_agent.py`: Generates quizzes based on a topic and difficulty.
    -   `recommendation_agent.py`: Suggests topics to study based on performance.
    -   `coach_agent.py`: Provides feedback on quiz results.
-   These agents are called by the FastAPI routes, which in turn are called by the frontend.

---

## 5. Security and Optimization

### 5.1. Data and Token Security

-   **Authentication Tokens (JWTs):** Handled by Supabase's secure, cookie-based session management. Not exposed to XSS attacks.
-   **User Data:** Protected by Supabase's **Row Level Security (RLS)**. Policies are defined in `migrations/` to ensure users can only access their own data.
-   **API Keys:** All secrets (Supabase service key, OpenRouter API key, JWT secret) are stored in environment variables (`.env`) and are not exposed to the frontend.

### 5.2. Production Readiness Improvements

-   **Rate Limiting:** The FastAPI backend uses `slowapi` to limit requests to AI-intensive endpoints (e.g., 10 requests/minute), preventing abuse.
-   **CORS:** The backend is configured with a strict `ALLOWED_ORIGINS` list, preventing requests from unauthorized domains.
-   **Input Sanitization:** All user inputs, especially those sent to the OpenRouter API, are sanitized to mitigate the risk of prompt injection attacks.

### 5.3. Gemini CLI Security Checks

The Gemini CLI was used extensively to audit and verify the codebase for security vulnerabilities. This included checks for:
-   Hardcoded secrets.
-   Insecure API endpoint configurations.
-   Missing authentication on sensitive routes.
-   Potential XSS and SQL injection vectors.

---

## 6. API and Data Flow

### 6.1. API Routes

The backend exposes several RESTful API endpoints. Key routes include:

-   `POST /study/retry`: Regenerates study materials for a topic and awards XP.
-   `GET /coach/feedback/{user_id}`: Provides AI-powered coaching and recommendations.
-   `GET /achievements/user/{user_id}/badges`: Fetches a user's unlocked badges.
-   `GET /progress/v2/user/{user_id}/stats`: Retrieves detailed user statistics.

For a complete list, see `docs/BACKEND_API_COMPLETE.md`.

### 6.2. Data Schemas

The core data schemas are defined in `SUPABASE_SCHEMA.sql`.

-   `users`: Stores user profile information, total XP, and level.
-   `user_topics`: Tracks progress for each topic (e.g., 'JavaScript Basics').
-   `quiz_scores`: Logs every quiz attempt with score, difficulty, and timestamp.
-   `xp_history`: An immutable log of all XP transactions.
-   `badges` & `user_badges`: Defines available badges and tracks which users have earned them.

### 6.3. OpenRouter API Rate Limits

A key constraint is the rate limit imposed by the free tier of the OpenRouter API. This affects how frequently users can generate new quizzes or get AI feedback. The application handles this gracefully by:
-   Implementing rate limiting on the backend.
-   Providing clear error messages to the user when a limit is exceeded.
-   Caching AI-generated content where possible.

---

## 7. Testing and Debugging

The Gemini CLI was instrumental in the testing and verification process. It was used to:

-   **Verify Missing Values:** Scan the codebase for potential null or undefined errors.
-   **Identify Entry Points:** Map out all API routes and frontend pages.
-   **Test API Connectivity:** Run `curl` commands to test backend endpoints.
-   **Ensure Consistency:** Check for discrepancies between frontend API calls and backend route definitions.
-   **Scan for Vulnerabilities:** Perform automated security scans.

### Test Credentials

A test user is available for local development and E2E testing:
-   **Email:** `test@studyquest.dev`
-   **Password:** `testuser123`

---

## 8. Deployment and Setup

### 8.1. Local Setup (MacBook)

1.  **Prerequisites:** Install Node.js (v18+), Python (v3.8+), and Git.
2.  **Clone Repository:** `git clone <repo_url>`
3.  **Supabase Setup:**
    -   Create a new project on [Supabase](https://supabase.com).
    -   In the Supabase SQL Editor, run the `SUPABASE_SCHEMA.sql` script.
    -   Run `migrations/CREATE_TEST_USER.sql`.
4.  **Configure Environment Variables:**
    -   Create `frontend/.env.local` and `backend/.env` from the `.example` files.
    -   Fill in your Supabase project URL, anon key, and service role key.
    -   Add your OpenRouter API key to `backend/.env`.
5.  **Install Dependencies:**
    -   `cd frontend && npm install`
    -   `cd backend && pip install -r requirements.txt`
6.  **Run Servers:**
    -   Frontend: `npm run dev` (runs on `http://localhost:3000`)
    -   Backend: `uvicorn main:app --reload` (runs on `http://localhost:8000`)

### 8.2. Vercel + Supabase Deployment

1.  **Frontend (Vercel):**
    -   Connect your Git repository to a new Vercel project.
    -   Add the `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` environment variables.
    -   Deploy.
2.  **Backend (Railway/Render):**
    -   Connect your Git repository to a new backend service.
    -   Set the start command to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
    -   Add all environment variables from `backend/.env`.
3.  **Supabase (Production):**
    -   Run the `migrations/UPDATE_RLS_POLICIES_PRODUCTION.sql` script to enforce strict authentication.

---

## 9. Known Issues and Future Scope

### 9.1. Limitations

-   **OpenRouter API Limits:** The primary limitation is the reliance on the free tier of the OpenRouter API, which restricts the frequency of AI-powered actions.
-   **Mock Data:** Some parts of the application may still use mock data for topics or quiz questions, which needs to be replaced with fully dynamic generation.

### 9.2. Future Improvements

-   **AI-Generated Quests:** Dynamically create personalized quests for users (e.g., "Achieve an 80% score in 3 different Python topics").
-   **Peer Challenges:** Allow users to challenge each other to quizzes.
-   **Adaptive XP System:** Adjust XP rewards based on user performance and topic difficulty more dynamically.
-   **Expanded Content:** Support for more content types, like flashcards and coding exercises.

---

## 10. Final Notes

StudyQuest is more than just a study tool; it's a proof-of-concept for a new way of learning. By making the process enjoyable, trackable, and interactive, we can empower learners to take control of their education and achieve their goals.

This MVP version establishes a stable and feature-rich core. While some AI-dependent features are constrained by API rate limits, the foundational architecture is robust and ready for future expansion. We believe in the power of open-source innovation and hope that StudyQuest can inspire others to build the future of learning.

**Begin your quest!**
