# Quiz Generation - Enhanced Features 🎯

## Overview

The quiz generation feature has been enhanced with three powerful ways to create quizzes:

### 1. 📚 From Saved Study Notes
Select from your previously generated AI study materials to create quizzes. This feature:
- Shows all your past study sessions
- Allows quick quiz generation from topics you've already studied
- Maintains consistency between study materials and quiz questions

### 2. 📄 Upload PDF
Upload a PDF document and AI will:
- Extract text content from the PDF
- Analyze the material
- Generate relevant quiz questions
- Support PDFs up to 10MB

### 3. ✍️ Custom Topic
Enter any topic and let AI generate quiz questions on the fly.

## How to Use

### Setup Required

1. **Run the SQL Migration** (One-time setup)
   ```sql
   -- Run this in Supabase SQL Editor
   -- File: migrations/ADD_STUDY_SESSIONS_TABLE.sql
   ```
   This creates the `study_sessions` table to store your generated notes.

2. **Backend must be running** with PDF support
   ```bash
   cd backend
   source venv/bin/activate
   pip install PyPDF2==3.0.1
   uvicorn main:app --reload --port 8000
   ```

3. **Frontend must be running**
   ```bash
   cd frontend
   npm run dev
   ```

### Using the Quiz Generator

1. Navigate to the Quiz page (`/quiz`)
2. Choose one of three options:

#### Option 1: From Saved Notes
- Click on the "FROM_SAVED_NOTES()" card
- Browse your previously generated study materials
- Click on any topic to generate a quiz from those notes
- The quiz will be based on the AI-generated key points and summary

#### Option 2: Upload PDF
- Click on the "UPLOAD_PDF()" card
- Choose a PDF file (max 10MB)
- Wait for AI to process the content
- Quiz questions will be generated from the PDF content

#### Option 3: Custom Topic
- Click on the "CUSTOM_TOPIC()" card  
- Enter any topic (e.g., "Python Functions", "World War II", "Photosynthesis")
- Click "GENERATE_QUIZ()"
- AI will generate both study notes and quiz questions

## Features

✅ **Saved Notes Integration**
- Automatically saves study notes when you use "Start New Study Session"
- Shows creation date for each saved topic
- Quick access to previously studied materials

✅ **PDF Processing**
- Extracts text from all pages
- Handles multi-page documents
- Intelligent chunking for optimal quiz generation
- Supports academic papers, textbooks, articles

✅ **Smart Quiz Generation**
- 5 questions per quiz
- Multiple choice format (A, B, C, D)
- Detailed explanations for each answer
- Progress tracking (X/5 answered)

✅ **Interactive Quiz Taking**
- Navigate between questions (Previous/Next)
- Visual progress indicators
- Answer validation before submission
- Detailed results page with score and performance breakdown

## Technical Details

### Database Schema
```sql
CREATE TABLE public.study_sessions (
  id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  topic TEXT NOT NULL,
  summary TEXT NOT NULL,
  key_points JSONB NOT NULL,
  quiz_questions JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### API Endpoints

**Generate Quiz from PDF:**
```
POST /quiz/generate-from-pdf
Content-Type: multipart/form-data
Authorization: Bearer <JWT_TOKEN>

Parameters:
- file: PDF file (max 10MB)
- num_questions: Number of questions (1-10, default: 5)

Response:
{
  "questions": [...],
  "metadata": {
    "num_questions": 5,
    "pdf_pages": 3,
    "content_length": 2340,
    "generation_time_ms": 2500,
    "filename": "document.pdf"
  }
}
```

**Get Saved Study Sessions:**
```
GET /study/sessions
Authorization: Bearer <JWT_TOKEN>

Response:
[
  {
    "id": "uuid",
    "topic": "Python Functions",
    "summary": "...",
    "key_points": ["..."],
    "created_at": "2025-11-06T..."
  }
]
```

### Frontend Components

**Quiz Page** (`/app/quiz/page.tsx`)
- Selection screen with 3 options
- Quiz taking interface
- Answer tracking and submission

**Result Page** (`/app/quiz/result/page.tsx`)
- Score display
- Performance breakdown
- Retry/Home options

## Limitations

- **PDF Size**: Maximum 10MB per file
- **PDF Type**: Text-based PDFs only (not scanned images)
- **Text Extraction**: Complex layouts may not extract perfectly
- **Questions**: Maximum 10 questions per quiz
- **API Rate Limits**: Free tier of OpenRouter has daily limits

## Troubleshooting

**"No saved notes yet"**
- Create study notes first using "Start New Study Session" on the Study page
- Notes are automatically saved to your account

**"Failed to process PDF"**
- Ensure PDF is text-based (not a scanned image)
- Check PDF size is under 10MB
- Try a simpler PDF first to test

**"Rate limit exceeded"**
- OpenRouter free tier is rate-limited
- Wait for rate limit to reset or add credits
- Cached results are used when available

**"Authentication required"**
- Log in again if session expired
- Check that backend is running
- Verify Supabase credentials

## Future Enhancements

Planned features:
- [ ] Support for Word documents (.docx)
- [ ] Difficulty level selection for quizzes
- [ ] Quiz history and analytics
- [ ] Export quiz results
- [ ] Share quizzes with friends
- [ ] Adaptive difficulty based on performance
- [ ] Timed quiz mode
- [ ] Image-based questions from PDF figures

## Migration Guide

If you already have the app running:

1. **Stop the backend**
2. **Update requirements.txt** (already done)
3. **Install PyPDF2**: `pip install PyPDF2==3.0.1`
4. **Run Supabase migration** (ADD_STUDY_SESSIONS_TABLE.sql)
5. **Restart backend**
6. **Frontend will auto-update** (Next.js hot reload)

Done! Your quiz feature is now enhanced with PDF support and saved notes integration.
