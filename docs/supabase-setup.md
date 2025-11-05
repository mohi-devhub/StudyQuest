# Supabase Database Schema Setup

## Users Table

The users table is automatically managed by Supabase Auth. However, you can extend it with additional fields.

### SQL Migration for Users Table Extension

Run this SQL in your Supabase SQL Editor:

```sql
-- Create a public users table that syncs with auth.users
CREATE TABLE IF NOT EXISTS public.users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policies
-- Users can read their own data
CREATE POLICY "Users can view own data"
  ON public.users
  FOR SELECT
  USING (auth.uid() = id);

-- Users can update their own data
CREATE POLICY "Users can update own data"
  ON public.users
  FOR UPDATE
  USING (auth.uid() = id);

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, created_at)
  VALUES (NEW.id, NEW.email, NEW.created_at);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to automatically create user record
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Function to handle user updates
CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
CREATE TRIGGER on_user_updated
  BEFORE UPDATE ON public.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_user_update();
```

### Additional Tables for StudyQuest

```sql
-- Study Sessions Table
CREATE TABLE IF NOT EXISTS public.study_sessions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  duration_minutes INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.study_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own study sessions"
  ON public.study_sessions
  FOR ALL
  USING (auth.uid() = user_id);

-- Quizzes Table
CREATE TABLE IF NOT EXISTS public.quizzes (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  title TEXT NOT NULL,
  description TEXT,
  questions JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.quizzes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own quizzes"
  ON public.quizzes
  FOR ALL
  USING (auth.uid() = user_id);

-- Progress Tracking Table
CREATE TABLE IF NOT EXISTS public.progress (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  topic TEXT NOT NULL,
  completion_status TEXT NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'completed'
  last_attempt TIMESTAMPTZ,
  avg_score DECIMAL(5,2) DEFAULT 0.0, -- Average score as percentage (0.00 - 100.00)
  total_attempts INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, topic) -- One progress record per user per topic
);

ALTER TABLE public.progress ENABLE ROW LEVEL SECURITY;

-- Users can view their own progress
CREATE POLICY "Users can view own progress"
  ON public.progress
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own progress
CREATE POLICY "Users can insert own progress"
  ON public.progress
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Users can update their own progress
CREATE POLICY "Users can update own progress"
  ON public.progress
  FOR UPDATE
  USING (auth.uid() = user_id);

-- Users can delete their own progress
CREATE POLICY "Users can delete own progress"
  ON public.progress
  FOR DELETE
  USING (auth.uid() = user_id);

-- XP Logs Table
CREATE TABLE IF NOT EXISTS public.xp_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  points INTEGER NOT NULL,
  reason TEXT NOT NULL, -- 'quiz_completed', 'study_session', 'daily_streak', etc.
  metadata JSONB DEFAULT '{}'::jsonb, -- Additional data like quiz score, topic, etc.
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.xp_logs ENABLE ROW LEVEL SECURITY;

-- Users can view their own XP logs
CREATE POLICY "Users can view own xp logs"
  ON public.xp_logs
  FOR SELECT
  USING (auth.uid() = user_id);

-- Users can insert their own XP logs
CREATE POLICY "Users can insert own xp logs"
  ON public.xp_logs
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- System/backend can insert XP logs (via service role key)
-- Note: This policy allows authenticated users to insert their own logs
-- For backend insertion, use the service role key which bypasses RLS

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON public.study_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_quizzes_user_id ON public.quizzes(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_user_id ON public.progress(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_topic ON public.progress(topic);
CREATE INDEX IF NOT EXISTS idx_progress_user_topic ON public.progress(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_id ON public.xp_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_xp_logs_timestamp ON public.xp_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_xp_logs_user_timestamp ON public.xp_logs(user_id, timestamp DESC);

-- Function to automatically update updated_at timestamp for progress
CREATE OR REPLACE FUNCTION public.update_progress_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_progress_updated
  BEFORE UPDATE ON public.progress
  FOR EACH ROW
  EXECUTE FUNCTION public.update_progress_timestamp();

-- View to get total XP per user
CREATE OR REPLACE VIEW public.user_total_xp AS
SELECT 
  user_id,
  SUM(points) as total_xp,
  COUNT(*) as total_activities,
  MAX(timestamp) as last_activity
FROM public.xp_logs
GROUP BY user_id;

-- Grant access to the view
ALTER VIEW public.user_total_xp SET (security_invoker = true);

-- RLS policy for the view
CREATE POLICY "Users can view own total XP"
  ON public.xp_logs
  FOR SELECT
  USING (auth.uid() = user_id);
```

## Setup Instructions

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy and paste the above SQL scripts
4. Run them in order
5. Verify the tables are created in the Table Editor

## Environment Variables

Make sure your `.env` file has:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

You can find these in: Settings → API → Project URL and Project API keys (anon/public)
