# Operations Runbook

This runbook provides operational procedures for monitoring, maintaining, and troubleshooting the StudyQuest application in production.

## Table of Contents

- [System Overview](#system-overview)
- [Health Monitoring](#health-monitoring)
- [Viewing Logs](#viewing-logs)
- [Common Issues and Solutions](#common-issues-and-solutions)
- [Performance Monitoring](#performance-monitoring)
- [Database Operations](#database-operations)
- [Security Operations](#security-operations)
- [Incident Response](#incident-response)
- [Maintenance Procedures](#maintenance-procedures)
- [Monitoring and Alerting Setup](#monitoring-and-alerting-setup)

## System Overview

### Architecture Components

| Component | Technology | Hosting | URL |
|-----------|-----------|---------|-----|
| Frontend | Next.js 14 | Vercel | https://your-app.vercel.app |
| Backend | FastAPI | Render | https://your-backend.onrender.com |
| Database | PostgreSQL | Supabase | https://your-project.supabase.co |
| AI Service | OpenRouter | External API | https://openrouter.ai |

### Service Dependencies

```
Frontend → Backend → Database (Supabase)
                  → AI Service (OpenRouter)
```

### Critical Endpoints

- **Frontend**: `/`, `/login`, `/study`, `/quiz`, `/progress`
- **Backend**: `/health`, `/health/detailed`, `/study/*`, `/quiz/*`, `/progress/*`
- **API Docs**: `/docs` (Swagger UI)

## Health Monitoring

### Checking Application Health

#### 1. Basic Health Check

**Backend:**
```bash
curl https://your-backend.onrender.com/health

# Expected Response:
{
  "status": "healthy",
  "timestamp": "2025-11-22T10:30:00.000Z"
}
```

**Frontend:**
```bash
curl https://your-app.vercel.app/api/health

# Expected Response:
{
  "status": "healthy",
  "backend": "connected",
  "supabase": "connected"
}
```

#### 2. Detailed Health Check

```bash
curl https://your-backend.onrender.com/health/detailed

# Expected Response:
{
  "status": "healthy",
  "timestamp": "2025-11-22T10:30:00.000Z",
  "dependencies": {
    "supabase": {
      "status": "healthy",
      "response_time_ms": 45
    },
    "openrouter": {
      "status": "healthy"
    }
  }
}
```

#### 3. Interpreting Health Status

| Status | Meaning | Action Required |
|--------|---------|-----------------|
| `healthy` | All systems operational | None |
| `degraded` | Some dependencies failing | Investigate failing dependencies |
| `unhealthy` | Critical failure | Immediate action required |

### Health Check Automation

**Automated Monitoring Script:**

```bash
#!/bin/bash
# health-check.sh - Run every 5 minutes via cron

BACKEND_URL="https://your-backend.onrender.com"
FRONTEND_URL="https://your-app.vercel.app"

# Check backend
backend_status=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/health)
if [ "$backend_status" != "200" ]; then
  echo "ALERT: Backend health check failed with status $backend_status"
  # Send alert (email, Slack, PagerDuty, etc.)
fi

# Check frontend
frontend_status=$(curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL/api/health)
if [ "$frontend_status" != "200" ]; then
  echo "ALERT: Frontend health check failed with status $frontend_status"
  # Send alert
fi

# Check detailed health
detailed=$(curl -s $BACKEND_URL/health/detailed)
overall_status=$(echo "$detailed" | jq -r '.status')
if [ "$overall_status" != "healthy" ]; then
  echo "ALERT: System status is $overall_status"
  echo "$detailed" | jq .
  # Send alert with details
fi
```

**Setup Cron Job:**
```bash
# Edit crontab
crontab -e

# Add health check (runs every 5 minutes)
*/5 * * * * /path/to/health-check.sh >> /var/log/studyquest-health.log 2>&1
```

### Docker Health Checks

If running with Docker:

```bash
# Check container health status
docker ps

# View health check logs
docker inspect studyquest-backend | grep -A 10 Health
docker inspect studyquest-frontend | grep -A 10 Health

# Manual health check
docker-compose exec backend curl http://localhost:8000/health
docker-compose exec frontend curl http://localhost:3000/api/health
```

## Viewing Logs

### Structured Logging Format

All logs are in JSON format for easy parsing:

```json
{
  "timestamp": "2025-11-22T10:30:00.000Z",
  "level": "INFO",
  "logger": "backend.agents.quiz_agent",
  "message": "Generated quiz for topic",
  "module": "adaptive_quiz_agent",
  "function": "generate_adaptive_quiz",
  "line": 45,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "topic": "Python",
  "difficulty": "medium"
}
```

### Backend Logs

#### Render Platform

**Via Dashboard:**
1. Go to Render Dashboard
2. Select studyquest-backend service
3. Click "Logs" tab
4. View real-time logs

**Via CLI:**
```bash
# Install Render CLI
npm install -g @render/cli

# View logs
render logs -s studyquest-backend

# Follow logs in real-time
render logs -s studyquest-backend -f

# Filter by time
render logs -s studyquest-backend --since 1h
```

#### Docker Deployment

```bash
# View all backend logs
docker-compose logs backend

# Follow logs in real-time
docker-compose logs -f backend

# View last 100 lines
docker-compose logs --tail=100 backend

# Filter by timestamp
docker-compose logs --since 2025-11-22T10:00:00 backend
```

#### Parsing JSON Logs

```bash
# Pretty print JSON logs
docker-compose logs backend | grep -o '{.*}' | jq .

# Filter by log level
docker-compose logs backend | grep -o '{.*}' | jq 'select(.level == "ERROR")'

# Filter by user_id
docker-compose logs backend | grep -o '{.*}' | jq 'select(.user_id == "123e4567")'

# Count errors in last hour
docker-compose logs --since 1h backend | grep -o '{.*}' | jq 'select(.level == "ERROR")' | wc -l
```

### Frontend Logs

#### Vercel Platform

**Via Dashboard:**
1. Go to Vercel Dashboard
2. Select studyquest-frontend project
3. Click "Logs" tab
4. View real-time logs

**Via CLI:**
```bash
# Install Vercel CLI
npm install -g vercel

# View logs
vercel logs studyquest-frontend

# Follow logs in real-time
vercel logs studyquest-frontend --follow

# Filter by time
vercel logs studyquest-frontend --since 1h
```

#### Docker Deployment

```bash
# View all frontend logs
docker-compose logs frontend

# Follow logs in real-time
docker-compose logs -f frontend

# Parse JSON logs
docker-compose logs frontend | grep -o '{.*}' | jq .
```

### Log Analysis

**Common Log Queries:**

```bash
# Find all errors in last hour
docker-compose logs --since 1h | grep -o '{.*}' | jq 'select(.level == "ERROR")'

# Find slow database queries (>500ms)
docker-compose logs backend | grep -o '{.*}' | jq 'select(.response_time_ms > 500)'

# Find failed authentication attempts
docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("authentication failed"))'

# Count requests by endpoint
docker-compose logs backend | grep -o '{.*}' | jq -r '.endpoint' | sort | uniq -c

# Find AI generation failures
docker-compose logs backend | grep -o '{.*}' | jq 'select(.logger | contains("agents")) | select(.level == "ERROR")'
```

### Log Retention

**Render:**
- Free tier: 7 days
- Paid tiers: 30+ days
- Export logs for long-term storage

**Vercel:**
- Hobby: 1 day
- Pro: 7 days
- Enterprise: Custom retention

**Docker:**
- Configure log rotation in docker-compose.yml:
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Common Issues and Solutions

### Issue 1: Service Unavailable (503)

**Symptoms:**
- Health check returns 503
- Users cannot access application
- "Service Unavailable" error

**Diagnosis:**
```bash
# Check service status
curl -I https://your-backend.onrender.com/health

# Check detailed health
curl https://your-backend.onrender.com/health/detailed

# View recent logs
render logs -s studyquest-backend --tail 100
```

**Solutions:**

1. **Service Crashed:**
   ```bash
   # Restart service (Render)
   # Dashboard → studyquest-backend → Manual Deploy → Redeploy
   
   # Or via Docker
   docker-compose restart backend
   ```

2. **Out of Memory:**
   ```bash
   # Check memory usage
   docker stats studyquest-backend
   
   # Increase memory limit in docker-compose.yml
   # Or upgrade Render plan
   ```

3. **Database Connection Failed:**
   ```bash
   # Verify Supabase credentials
   # Check SUPABASE_URL and SUPABASE_KEY
   
   # Test connection
   curl -X GET "https://YOUR_PROJECT.supabase.co/rest/v1/users?select=user_id&limit=1" \
     -H "apikey: YOUR_ANON_KEY"
   ```

### Issue 2: Slow Response Times

**Symptoms:**
- API requests taking >3 seconds
- Users reporting slow page loads
- Timeout errors

**Diagnosis:**
```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://your-backend.onrender.com/health/detailed

# curl-format.txt:
# time_total: %{time_total}s
# time_connect: %{time_connect}s
# time_starttransfer: %{time_starttransfer}s

# Check database query times
docker-compose logs backend | grep -o '{.*}' | jq 'select(.response_time_ms) | {endpoint, response_time_ms}'
```

**Solutions:**

1. **Database Queries Slow:**
   ```bash
   # Check for missing indexes
   # Connect to Supabase SQL Editor
   # Run: EXPLAIN ANALYZE SELECT * FROM users WHERE user_id = '...';
   
   # Add indexes if needed (see migrations/ADD_PERFORMANCE_INDEXES.sql)
   ```

2. **AI Requests Slow:**
   ```bash
   # Check AI cache hit rate
   docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("cache"))'
   
   # Verify cache is enabled
   # Check backend/utils/ai_cache.py
   ```

3. **Connection Pool Exhausted:**
   ```bash
   # Increase pool size in backend/.env
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=10
   
   # Restart backend
   docker-compose restart backend
   ```

### Issue 3: Authentication Failures

**Symptoms:**
- Users cannot log in
- "Invalid token" errors
- 401 Unauthorized responses

**Diagnosis:**
```bash
# Check auth logs
docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("auth"))'

# Test JWT validation
curl -X POST https://your-backend.onrender.com/study/retry \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python"}'
```

**Solutions:**

1. **JWT Secret Mismatch:**
   ```bash
   # Verify JWT_SECRET matches Supabase
   # Supabase Dashboard → Settings → API → JWT Settings
   
   # Update backend/.env
   JWT_SECRET=your_supabase_jwt_secret
   
   # Restart backend
   ```

2. **Expired Tokens:**
   ```bash
   # Users need to log out and log back in
   # Or implement token refresh logic
   ```

3. **CORS Issues:**
   ```bash
   # Update ALLOWED_ORIGINS in backend/.env
   ALLOWED_ORIGINS=https://your-app.vercel.app,https://www.your-domain.com
   
   # Restart backend
   ```

### Issue 4: AI Generation Failures

**Symptoms:**
- Quiz generation fails
- "AI service unavailable" errors
- Empty responses from AI endpoints

**Diagnosis:**
```bash
# Check AI logs
docker-compose logs backend | grep -o '{.*}' | jq 'select(.logger | contains("agents"))'

# Test OpenRouter API
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_OPENROUTER_KEY"
```

**Solutions:**

1. **Invalid API Key:**
   ```bash
   # Verify OPENROUTER_API_KEY in backend/.env
   # Get new key from https://openrouter.ai/keys
   
   # Update and restart
   ```

2. **Rate Limit Exceeded:**
   ```bash
   # Check rate limit headers in logs
   # Wait for rate limit to reset
   # Or upgrade OpenRouter plan
   ```

3. **Model Unavailable:**
   ```bash
   # Check if model is available
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer YOUR_KEY" | jq '.data[] | select(.id | contains("gemini"))'
   
   # Update model in agent code if needed
   ```

### Issue 5: Database Connection Errors

**Symptoms:**
- "Connection refused" errors
- "Too many connections" errors
- Database queries timing out

**Diagnosis:**
```bash
# Check database logs
docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("database") or contains("supabase"))'

# Test Supabase connection
curl -X GET "https://YOUR_PROJECT.supabase.co/rest/v1/users?select=user_id&limit=1" \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Authorization: Bearer YOUR_ANON_KEY"
```

**Solutions:**

1. **Connection Pool Exhausted:**
   ```bash
   # Increase pool size
   # backend/.env:
   DB_POOL_SIZE=20
   DB_MAX_OVERFLOW=10
   DB_POOL_TIMEOUT=60
   
   # Restart backend
   ```

2. **Supabase Paused (Free Tier):**
   ```bash
   # Free tier pauses after inactivity
   # Wake up by visiting Supabase dashboard
   # Or upgrade to paid tier
   ```

3. **Network Issues:**
   ```bash
   # Check Supabase status
   # https://status.supabase.com
   
   # Test connectivity
   ping YOUR_PROJECT.supabase.co
   ```

## Performance Monitoring

### Key Metrics to Monitor

1. **Response Times**
   - Target: <500ms for API endpoints
   - Target: <3s for AI generation

2. **Error Rates**
   - Target: <1% error rate
   - Alert on: >5% error rate

3. **Database Performance**
   - Target: <100ms for queries
   - Alert on: >500ms for queries

4. **Memory Usage**
   - Backend: <400MB (limit: 512MB)
   - Frontend: <200MB (limit: 256MB)

5. **CPU Usage**
   - Backend: <70% average
   - Frontend: <50% average

### Monitoring Commands

**Response Time Monitoring:**
```bash
# Monitor endpoint response times
while true; do
  time=$(curl -w "%{time_total}" -o /dev/null -s https://your-backend.onrender.com/health)
  echo "$(date): Health check took ${time}s"
  sleep 60
done
```

**Error Rate Monitoring:**
```bash
# Count errors in last hour
errors=$(docker-compose logs --since 1h backend | grep -o '{.*}' | jq 'select(.level == "ERROR")' | wc -l)
total=$(docker-compose logs --since 1h backend | grep -o '{.*}' | wc -l)
error_rate=$(echo "scale=2; $errors / $total * 100" | bc)
echo "Error rate: ${error_rate}%"
```

**Resource Usage Monitoring:**
```bash
# Docker stats
docker stats --no-stream studyquest-backend studyquest-frontend

# Continuous monitoring
docker stats studyquest-backend studyquest-frontend
```

### Performance Optimization

**Database Optimization:**
```sql
-- Check slow queries in Supabase
-- Dashboard → Database → Query Performance

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_user_topics_user_id ON user_topics(user_id);
CREATE INDEX IF NOT EXISTS idx_quiz_scores_user_topic ON quiz_scores(user_id, topic);
CREATE INDEX IF NOT EXISTS idx_xp_history_user_created ON xp_history(user_id, created_at DESC);
```

**Cache Optimization:**
```bash
# Check AI cache hit rate
docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("cache hit"))'

# Increase cache TTL if needed
# backend/utils/ai_cache.py: ttl_seconds=3600
```

**Connection Pool Tuning:**
```bash
# Adjust based on load
# backend/.env:
DB_POOL_SIZE=15  # Increase for high traffic
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30
```

## Database Operations

### Backup Procedures

**Supabase Automatic Backups:**
- Free tier: Daily backups (7-day retention)
- Pro tier: Daily backups (30-day retention)
- Enterprise: Custom backup schedule

**Manual Backup:**
```bash
# Export database via Supabase CLI
supabase db dump -f backup-$(date +%Y%m%d).sql

# Or via pg_dump (if direct access)
pg_dump -h YOUR_PROJECT.supabase.co -U postgres -d postgres > backup.sql
```

### Running Migrations

```bash
# Connect to Supabase SQL Editor
# Paste migration SQL and execute

# Or via Supabase CLI
supabase db push

# Verify migration
supabase db diff
```

### Database Maintenance

**Check Table Sizes:**
```sql
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Vacuum and Analyze:**
```sql
-- Run periodically to optimize performance
VACUUM ANALYZE;

-- For specific tables
VACUUM ANALYZE users;
VACUUM ANALYZE quiz_scores;
```

**Check Index Usage:**
```sql
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Security Operations

### Security Monitoring

**Check for Failed Auth Attempts:**
```bash
# View failed login attempts
docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("authentication failed"))'

# Count failed attempts by IP
docker-compose logs backend | grep -o '{.*}' | jq 'select(.message | contains("authentication failed")) | .ip' | sort | uniq -c
```

**Monitor Rate Limiting:**
```bash
# Check rate limit violations
docker-compose logs backend | grep -o '{.*}' | jq 'select(.status_code == 429)'

# Count by endpoint
docker-compose logs backend | grep -o '{.*}' | jq 'select(.status_code == 429) | .endpoint' | sort | uniq -c
```

**Scan for Vulnerabilities:**
```bash
# Run security scan workflow manually
gh workflow run security.yml

# Check scan results
gh run list --workflow=security.yml
```

### Security Incident Response

**If Credentials Compromised:**

1. **Rotate API Keys:**
   ```bash
   # OpenRouter: Generate new key at https://openrouter.ai/keys
   # Update backend/.env and redeploy
   
   # Supabase: Generate new keys in dashboard
   # Update both backend/.env and frontend/.env.local
   ```

2. **Revoke JWT Tokens:**
   ```bash
   # Update JWT_SECRET in backend/.env
   # Forces all users to re-authenticate
   ```

3. **Review Access Logs:**
   ```bash
   # Check for suspicious activity
   docker-compose logs backend | grep -o '{.*}' | jq 'select(.timestamp > "2025-11-22T00:00:00")'
   ```

**If DDoS Attack:**

1. **Enable Rate Limiting:**
   ```python
   # Already implemented in backend
   # Adjust limits in backend/main.py if needed
   ```

2. **Block IPs:**
   ```bash
   # Add to Render/Vercel firewall rules
   # Or use Cloudflare for DDoS protection
   ```

## Incident Response

### Incident Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| P0 - Critical | Complete outage | Immediate | Service down, data loss |
| P1 - High | Major degradation | <15 minutes | Auth broken, AI failing |
| P2 - Medium | Partial degradation | <1 hour | Slow responses, some errors |
| P3 - Low | Minor issues | <4 hours | UI glitches, non-critical bugs |

### Incident Response Checklist

**For P0/P1 Incidents:**

1. **Acknowledge:**
   - [ ] Confirm incident
   - [ ] Notify team
   - [ ] Update status page

2. **Assess:**
   - [ ] Check health endpoints
   - [ ] Review logs
   - [ ] Identify root cause

3. **Mitigate:**
   - [ ] Apply immediate fix
   - [ ] Rollback if needed
   - [ ] Verify resolution

4. **Communicate:**
   - [ ] Update stakeholders
   - [ ] Post incident report
   - [ ] Document lessons learned

### Escalation Procedures

1. **On-Call Engineer** (0-15 min)
   - Initial response
   - Basic troubleshooting
   - Escalate if needed

2. **Senior Engineer** (15-30 min)
   - Complex issues
   - Architecture decisions
   - Escalate if needed

3. **Engineering Lead** (30+ min)
   - Critical decisions
   - External communication
   - Post-mortem coordination

## Maintenance Procedures

### Scheduled Maintenance

**Weekly Tasks:**
- [ ] Review error logs
- [ ] Check performance metrics
- [ ] Verify backup completion
- [ ] Update dependencies (if needed)

**Monthly Tasks:**
- [ ] Review security scan results
- [ ] Analyze usage patterns
- [ ] Optimize database queries
- [ ] Update documentation

**Quarterly Tasks:**
- [ ] Conduct security audit
- [ ] Review and update runbook
- [ ] Capacity planning
- [ ] Disaster recovery drill

### Dependency Updates

**Backend Dependencies:**
```bash
# Check for updates
cd backend
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements.txt
pip freeze > requirements.txt

# Test and deploy
pytest
git commit -am "Update dependencies"
git push
```

**Frontend Dependencies:**
```bash
# Check for updates
cd frontend
npm outdated

# Update specific package
npm update package-name

# Update all (careful!)
npm update

# Test and deploy
npm test
npm run build
git commit -am "Update dependencies"
git push
```

### Database Maintenance

**Weekly:**
```sql
-- Analyze tables for query optimization
ANALYZE users;
ANALYZE quiz_scores;
ANALYZE xp_history;
```

**Monthly:**
```sql
-- Vacuum to reclaim space
VACUUM ANALYZE;

-- Reindex if needed
REINDEX TABLE users;
```

## Monitoring and Alerting Setup

### Recommended Monitoring Tools

1. **Uptime Monitoring:**
   - UptimeRobot (free tier available)
   - Pingdom
   - StatusCake

2. **Application Performance:**
   - New Relic
   - Datadog
   - Sentry (error tracking)

3. **Log Management:**
   - Logtail
   - Papertrail
   - Logz.io

### Setting Up Alerts

**UptimeRobot Example:**

1. Create account at https://uptimerobot.com
2. Add monitors:
   - Backend health: `https://your-backend.onrender.com/health`
   - Frontend health: `https://your-app.vercel.app/api/health`
3. Configure alerts:
   - Email notifications
   - Slack integration
   - SMS for critical alerts

**Sentry for Error Tracking:**

```bash
# Install Sentry
cd backend
pip install sentry-sdk

cd frontend
npm install @sentry/nextjs
```

```python
# backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    traces_sample_rate=0.1,
    environment="production"
)
```

```typescript
// frontend/sentry.client.config.ts
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
});
```

### Alert Thresholds

**Recommended Thresholds:**

| Metric | Warning | Critical |
|--------|---------|----------|
| Response Time | >1s | >3s |
| Error Rate | >2% | >5% |
| CPU Usage | >70% | >90% |
| Memory Usage | >70% | >90% |
| Disk Usage | >80% | >95% |
| Uptime | <99% | <95% |

### On-Call Setup

**PagerDuty Integration:**

1. Create PagerDuty account
2. Set up escalation policy
3. Configure integrations:
   - UptimeRobot → PagerDuty
   - Sentry → PagerDuty
   - GitHub Actions → PagerDuty

**On-Call Schedule:**
- Primary: 24/7 coverage
- Secondary: Backup escalation
- Rotation: Weekly or bi-weekly

## Additional Resources

- [Docker Deployment Guide](./DOCKER_DEPLOYMENT.md)
- [CI/CD Guide](./CICD_GUIDE.md)
- [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md)
- [Security Documentation](../security/)
- [API Documentation](../BACKEND_API_COMPLETE.md)

## Support Contacts

- **Engineering Lead**: [email]
- **DevOps Team**: [email]
- **Security Team**: [email]
- **On-Call**: [PagerDuty/phone]

---

**Last Updated**: 2025-11-22  
**Version**: 1.0.0  
**Maintained By**: DevOps Team
