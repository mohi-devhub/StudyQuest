# Quick Setup: Progress & XP Tables in Supabase

This guide will help you quickly set up the progress tracking and XP system in your Supabase project.

## Prerequisites

- Supabase project created
- Access to Supabase SQL Editor
- Basic users table already set up (from docs/supabase-setup.md)

## Setup Steps

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase project dashboard
2. Click on **SQL Editor** in the left sidebar
3. Click **New query**

### Step 2: Run the Migration

Copy the entire contents of `backend/migrations/001_create_progress_xp_tables.sql` and paste into the SQL editor.

Click **Run** to execute the migration.

### Step 3: Verify Tables Created

After running the migration, verify in the **Table Editor**:

**Expected tables:**
- ✅ `progress` - User progress tracking
- ✅ `xp_logs` - XP earning history

**Expected view:**
- ✅ `user_total_xp` - Aggregated XP per user

### Step 4: Verify RLS Policies

Go to **Authentication** → **Policies**

**Progress table should have 4 policies:**
- ✅ Users can view own progress (SELECT)
- ✅ Users can insert own progress (INSERT)
- ✅ Users can update own progress (UPDATE)
- ✅ Users can delete own progress (DELETE)

**XP Logs table should have 2 policies:**
- ✅ Users can view own xp logs (SELECT)
- ✅ Users can insert own xp logs (INSERT)

### Step 5: Test with Sample Data

Run this test query to insert sample progress:

```sql
-- Replace 'your-user-uuid' with actual user ID from auth.users
INSERT INTO progress (user_id, topic, completion_status, last_attempt, avg_score, total_attempts)
VALUES (
  'your-user-uuid',
  'Test Topic',
  'completed',
  NOW(),
  85.5,
  1
);
```

Test XP log insertion:

```sql
-- Replace 'your-user-uuid' with actual user ID
INSERT INTO xp_logs (user_id, points, reason, metadata)
VALUES (
  'your-user-uuid',
  100,
  'quiz_completed',
  '{"topic": "Test Topic", "score": 85.5}'::jsonb
);
```

### Step 6: Verify Data

Query the data:

```sql
-- Check progress
SELECT * FROM progress WHERE user_id = 'your-user-uuid';

-- Check XP logs
SELECT * FROM xp_logs WHERE user_id = 'your-user-uuid';

-- Check total XP
SELECT * FROM user_total_xp WHERE user_id = 'your-user-uuid';
```

### Step 7: Test Helper Functions

Test the progress update function:

```sql
SELECT update_progress_after_quiz(
  'your-user-uuid',
  'Test Topic',
  90.0,
  'completed'
);
```

Test the XP award function:

```sql
SELECT award_xp(
  'your-user-uuid',
  100,
  'quiz_completed',
  '{"topic": "Test Topic", "score": 90.0}'::jsonb
);
```

## Verification Checklist

After setup, verify:

- [ ] Tables exist: `progress`, `xp_logs`
- [ ] View exists: `user_total_xp`
- [ ] RLS enabled on both tables
- [ ] 6 total RLS policies created
- [ ] Indexes created (check with `\d+ progress` and `\d+ xp_logs`)
- [ ] Functions work: `update_progress_after_quiz`, `award_xp`
- [ ] Trigger works: `on_progress_updated` (updates `updated_at`)
- [ ] Sample data inserts successfully
- [ ] Sample data queries return correct results

## Common Issues

### Issue: "relation does not exist"
**Solution:** Make sure you're running queries in the SQL Editor, not in the Table Editor filter box.

### Issue: "permission denied"
**Solution:** Ensure RLS policies are created. The migration script includes all policies.

### Issue: "duplicate key value violates unique constraint"
**Solution:** There's already a progress record for this user-topic combination. Use UPDATE instead of INSERT.

### Issue: "function does not exist"
**Solution:** Ensure the entire migration ran successfully. Re-run the function creation section.

## Next Steps

After successful setup:

1. Update your `.env` file with Supabase credentials
2. Start the FastAPI backend: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
3. Test the progress endpoints: `/progress/stats`, `/progress/xp`
4. Complete a quiz to see progress tracking in action

## API Testing

Test the new endpoints with curl:

```bash
# Get user's progress stats
curl -X GET http://localhost:8000/progress/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get total XP
curl -X GET http://localhost:8000/progress/xp \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get XP logs
curl -X GET http://localhost:8000/progress/xp/logs?limit=10 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Database Diagram

```
┌─────────────────┐
│   auth.users    │
│  (Supabase)     │
└────────┬────────┘
         │
         │ Foreign Key (CASCADE DELETE)
         │
    ┌────┴─────────────────────────┐
    │                              │
    ▼                              ▼
┌──────────┐                  ┌──────────┐
│ progress │                  │ xp_logs  │
├──────────┤                  ├──────────┤
│ user_id  │◄────┐           │ user_id  │
│ topic    │     │           │ points   │
│ status   │     │           │ reason   │
│ avg_score│     │           │ metadata │
│ attempts │     │           │ timestamp│
└──────────┘     │           └──────────┘
                 │                 │
                 │                 │
                 │           ┌─────▼─────────┐
                 │           │ user_total_xp │
                 │           │   (VIEW)      │
                 │           ├───────────────┤
                 └───────────┤ user_id       │
                             │ total_xp      │
                             │ total_activities
                             └───────────────┘
```

## Support

For issues or questions:
- Check docs/progress-tracking.md for detailed documentation
- Review backend/utils/progress_tracker.py for Python utilities
- Review backend/routes/progress.py for API implementation
