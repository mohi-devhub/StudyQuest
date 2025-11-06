# StudyQuest Documentation

## Quick Links
- [Setup Guide](./SETUP_GUIDE.md) - Complete installation instructions
- [Backend API](./BACKEND_API_COMPLETE.md) - All API endpoints reference
- [Quiz Features](./QUIZ_ENHANCED_FEATURES.md) - Quiz generation capabilities

## Features Overview

### 🎯 Core Features
- **AI-Powered Study Notes**: Generate comprehensive study materials on any topic
- **Adaptive Quizzes**: Three quiz generation modes (saved notes, PDF upload, custom topic)
- **Progress Tracking**: XP system with levels and detailed analytics
- **Achievements**: Unlock badges based on learning milestones
- **AI Coach**: Personalized feedback and study recommendations

### 📚 Quiz Generation Modes
1. **From Saved Notes**: Quick access to previously generated study materials
2. **Upload PDF**: Extract quiz questions from PDF documents (max 10MB)
3. **Custom Topic**: Enter any topic for instant quiz generation

### 🔒 Security Features
- JWT authentication via Supabase
- Row Level Security (RLS) on all database tables
- Rate limiting on API endpoints
- CORS protection with whitelist
- Security headers (XSS, CSRF, Clickjacking protection)
- No secrets in code (environment variables only)

## Project Structure

```
StudyQuest/
├── backend/              # FastAPI backend
│   ├── agents/          # AI agents (quiz, research, coach)
│   ├── routes/          # API endpoints
│   ├── utils/           # Authentication & helpers
│   └── main.py          # Application entry point
├── frontend/            # Next.js frontend
│   ├── app/            # Pages (study, quiz, progress, etc.)
│   ├── components/     # Reusable UI components
│   └── lib/            # Utilities and hooks
├── migrations/         # Database migrations
└── docs/              # Documentation
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **AI**: OpenRouter API (Claude, Llama models)
- **Database**: Supabase (PostgreSQL)
- **Auth**: Supabase Auth (JWT)
- **Rate Limiting**: SlowAPI
- **PDF Processing**: PyPDF2

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Auth**: Supabase Client
- **State**: React Hooks

## Environment Variables

### Backend (.env)
```bash
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENROUTER_API_KEY=your_openrouter_key
ALLOWED_ORIGINS=http://localhost:3001
ENVIRONMENT=development
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Setup

### Required Tables
1. **study_sessions** - Stores AI-generated study materials
2. **user_progress** - Tracks XP, levels, and quiz attempts
3. **achievements** - User badge unlocks
4. **leaderboard** - Global rankings

### Run Migrations
```bash
# In Supabase SQL Editor
1. Execute migrations/ADD_STUDY_SESSIONS_TABLE.sql
2. Execute other migrations as needed
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user

### Study
- `POST /study` - Generate AI study notes

### Quiz
- `POST /quiz` - Generate quiz from topic
- `POST /quiz/generate-from-topic` - Generate from structured notes
- `POST /quiz/generate-from-pdf` - Generate from PDF upload

### Progress
- `GET /progress/v2/{user_id}` - Get user progress and stats
- `POST /progress/v2/quiz-result` - Submit quiz results

### Achievements
- `GET /achievements/{user_id}` - Get user achievements

### Coach
- `GET /coach/feedback/{user_id}` - Get personalized feedback

## Development

### Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing

### Test Quiz Features
1. **Custom Topic**: Enter "Python Functions" → Generate Quiz
2. **PDF Upload**: Upload text-based PDF → Generate Quiz
3. **Saved Notes**: Create study session first → Select from saved notes

## Deployment Checklist

- [ ] Set production environment variables
- [ ] Update ALLOWED_ORIGINS for production domains
- [ ] Enable HTTPS and HSTS headers
- [ ] Run database migrations on production
- [ ] Test authentication flow
- [ ] Verify rate limiting is active
- [ ] Check security headers are applied

## Known Limitations

- **OpenRouter Free Tier**: Rate limited (add credits for production)
- **PDF Processing**: Text-based PDFs only, 10MB max
- **Browser Support**: Modern browsers only (ES6+)

## Troubleshooting

### "Failed to load saved sessions"
→ Run the ADD_STUDY_SESSIONS_TABLE.sql migration

### "Rate limit exceeded"
→ Wait for OpenRouter rate limit reset or add credits

### "Authentication required"
→ Check Supabase credentials and JWT token

### "Failed to process PDF"
→ Ensure PDF is text-based and under 10MB

## Contributing

1. Check for security issues before committing
2. Test authentication flows
3. Validate environment variables
4. Update documentation for new features

## License

MIT License - See LICENSE file for details

---

**Last Updated**: January 2025
**Version**: 1.0.0
**Status**: Production Ready
