# CI/CD Guide

This guide covers the Continuous Integration and Continuous Deployment (CI/CD) pipelines for StudyQuest using GitHub Actions.

## Table of Contents

- [Overview](#overview)
- [GitHub Actions Workflows](#github-actions-workflows)
- [Setting Up CI/CD](#setting-up-cicd)
- [Configuring Secrets](#configuring-secrets)
- [Deployment Process](#deployment-process)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring Deployments](#monitoring-deployments)
- [Troubleshooting](#troubleshooting)

## Overview

StudyQuest uses three main GitHub Actions workflows:

1. **Test Suite** (`test.yml`) - Runs on every push and PR
2. **Deploy to Production** (`deploy.yml`) - Runs on pushes to `main` branch
3. **Security Scan** (`security.yml`) - Runs weekly and on PRs

### CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Code Push/PR                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Test Suite Workflow                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Backend Tests   │      │  Frontend Tests  │            │
│  ├──────────────────┤      ├──────────────────┤            │
│  │ • pytest         │      │ • ESLint         │            │
│  │ • Coverage       │      │ • TypeScript     │            │
│  │ • pip-audit      │      │ • Jest           │            │
│  └──────────────────┘      │ • npm audit      │            │
│                            │ • Build check    │            │
│                            └──────────────────┘            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ (if main branch)
┌─────────────────────────────────────────────────────────────┐
│            Deploy to Production Workflow                     │
├─────────────────────────────────────────────────────────────┤
│  1. Wait for Tests to Pass                                   │
│  2. Deploy Backend (Render)                                  │
│     • Trigger deploy hook                                    │
│     • Basic health check                                     │
│     • Detailed health check                                  │
│     • Verify dependencies                                    │
│  3. Deploy Frontend (Vercel)                                 │
│     • Build and deploy                                       │
│     • Frontend health check                                  │
│     • Backend connectivity check                             │
│     • Smoke tests                                            │
│  4. Post-Deployment Verification                             │
│  5. Notify Status                                            │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Security Scan Workflow                          │
│              (Weekly + PRs)                                  │
├─────────────────────────────────────────────────────────────┤
│  • Dependency vulnerability scan                             │
│  • Secret scanning                                           │
│  • Code security analysis                                    │
└─────────────────────────────────────────────────────────────┘
```

## GitHub Actions Workflows

### 1. Test Suite Workflow (`test.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Backend Tests Job:**
```yaml
Steps:
1. Checkout code
2. Set up Python 3.11
3. Install dependencies (with caching)
4. Run pytest with coverage
5. Run pip-audit security scan
6. Upload coverage to Codecov
```

**Frontend Tests Job:**
```yaml
Steps:
1. Checkout code
2. Set up Node.js 18
3. Install dependencies (with caching)
4. Run ESLint
5. Run TypeScript type checking
6. Run Jest tests
7. Run npm audit security scan
8. Build check (verify production build works)
```

**Key Features:**
- Parallel execution (backend and frontend run simultaneously)
- Dependency caching for faster builds
- Coverage reporting
- Security audits
- Build verification

### 2. Deploy to Production Workflow (`deploy.yml`)

**Triggers:**
- Push to `main` branch
- Manual trigger via `workflow_dispatch`

**Jobs:**

#### Job 1: Check Tests
```yaml
Purpose: Wait for test workflow to complete successfully
- Waits for "Backend Tests" to pass
- Waits for "Frontend Tests" to pass
- Blocks deployment if tests fail
```

#### Job 2: Deploy Backend
```yaml
Steps:
1. Trigger Render deployment via webhook
2. Wait 60 seconds for deployment
3. Basic health check (/health endpoint)
   - Retries up to 10 times
   - 10-second intervals
4. Detailed health check (/health/detailed)
   - Verifies overall status
   - Checks Supabase dependency
   - Checks OpenRouter dependency
5. Rollback notification if health checks fail
6. Generate deployment summary
```

#### Job 3: Deploy Frontend
```yaml
Steps:
1. Install Vercel CLI
2. Pull Vercel environment configuration
3. Build project for production
4. Deploy to Vercel
5. Wait 20 seconds for stabilization
6. Frontend health check
7. Verify backend connectivity
8. Run smoke tests (homepage, login page)
9. Rollback notification if checks fail
10. Generate deployment summary
```

#### Job 4: Post-Deployment Verification
```yaml
Purpose: Final end-to-end verification
- Runs after both deployments succeed
- Comprehensive health checks
- Creates deployment summary
```

#### Job 5: Notify Deployment Status
```yaml
Purpose: Final status notification
- Checks all job results
- Reports overall deployment status
- Fails if any job failed
```

### 3. Security Scan Workflow (`security.yml`)

**Triggers:**
- Weekly on Mondays at 9 AM UTC (cron schedule)
- Pull requests to `main` or `develop`
- Manual trigger via `workflow_dispatch`

**Jobs:**

#### Job 1: Dependency Scan
```yaml
Steps:
1. Scan backend with pip-audit
   - Generates JSON report
   - Uploads as artifact
2. Scan frontend with npm audit
   - Generates JSON report
   - Uploads as artifact
3. Check for critical vulnerabilities
```

#### Job 2: Secret Scan
```yaml
Steps:
1. Run custom secret scanner (Python utility)
2. Run TruffleHog for verified secrets
3. Upload scan results as artifacts
```

#### Job 3: Code Security Scan
```yaml
Steps:
1. Run Bandit on Python code
   - Security issue detection
   - JSON report generation
2. Run ESLint security scan on TypeScript/JavaScript
   - Security-focused linting
   - JSON report generation
3. Upload results as artifacts
```

#### Job 4: Security Summary
```yaml
Purpose: Aggregate results
- Generates summary report
- Checks all scan statuses
- Reports any issues
```

## Setting Up CI/CD

### Prerequisites

1. **GitHub Repository**: Code hosted on GitHub
2. **Render Account**: For backend deployment
3. **Vercel Account**: For frontend deployment
4. **Supabase Project**: Database and authentication

### Initial Setup

#### 1. Fork/Clone Repository

```bash
git clone <repository-url>
cd studyquest
```

#### 2. Enable GitHub Actions

GitHub Actions are automatically enabled for repositories. Verify:
1. Go to repository → Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected

#### 3. Set Up Render (Backend)

1. Create Render account at https://render.com
2. Create new Web Service
3. Connect GitHub repository
4. Configure service:
   - **Name**: studyquest-backend
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
5. Add environment variables (see [Configuring Secrets](#configuring-secrets))
6. Get deploy hook URL:
   - Settings → Deploy Hook
   - Copy the webhook URL

#### 4. Set Up Vercel (Frontend)

1. Create Vercel account at https://vercel.com
2. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```
3. Link project:
   ```bash
   cd frontend
   vercel link
   ```
4. Get Vercel token:
   - Account Settings → Tokens
   - Create new token
   - Copy token value

#### 5. Configure Branch Protection

Protect the `main` branch:
1. Repository → Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Status checks: "Backend Tests", "Frontend Tests"
   - ✅ Require pull request reviews before merging

## Configuring Secrets

GitHub Actions requires secrets for deployment and testing.

### Adding Secrets to GitHub

1. Go to repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret below

### Required Secrets

#### Backend/Testing Secrets

| Secret Name | Description | Where to Get |
|------------|-------------|--------------|
| `SUPABASE_URL` | Supabase project URL | Supabase Dashboard → Settings → API |
| `SUPABASE_KEY` | Supabase anon key | Supabase Dashboard → Settings → API |
| `OPENROUTER_API_KEY` | OpenRouter API key | https://openrouter.ai/keys |
| `JWT_SECRET` | Supabase JWT secret | Supabase Dashboard → Settings → API → JWT Settings |

#### Frontend Secrets

| Secret Name | Description | Where to Get |
|------------|-------------|--------------|
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL | Same as backend |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key | Same as backend |

#### Deployment Secrets

| Secret Name | Description | Where to Get |
|------------|-------------|--------------|
| `RENDER_DEPLOY_HOOK_URL` | Render deploy webhook | Render Dashboard → Settings → Deploy Hook |
| `RENDER_BACKEND_URL` | Deployed backend URL | Render Dashboard (e.g., https://studyquest-backend.onrender.com) |
| `VERCEL_TOKEN` | Vercel authentication token | Vercel Account Settings → Tokens |

### Verifying Secrets

After adding secrets, verify they're configured:

```bash
# List secrets (names only, values are hidden)
gh secret list
```

### Environment-Specific Secrets

For staging vs production:

1. Use GitHub Environments:
   - Settings → Environments
   - Create "staging" and "production" environments
   - Add environment-specific secrets

2. Update workflow to use environments:
   ```yaml
   deploy-backend:
     environment: production
     steps:
       # deployment steps
   ```

## Deployment Process

### Automatic Deployment

Deployments happen automatically when code is pushed to `main`:

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and commit
git add .
git commit -m "Add new feature"

# 3. Push and create PR
git push origin feature/my-feature
# Create PR on GitHub

# 4. Tests run automatically on PR
# Review test results in PR checks

# 5. Merge PR to main
# Deployment starts automatically

# 6. Monitor deployment
# Check Actions tab on GitHub
```

### Manual Deployment

Trigger deployment manually:

1. **Via GitHub UI:**
   - Go to Actions tab
   - Select "Deploy to Production" workflow
   - Click "Run workflow"
   - Select branch (usually `main`)
   - Click "Run workflow"

2. **Via GitHub CLI:**
   ```bash
   gh workflow run deploy.yml
   ```

### Deployment Stages

#### Stage 1: Pre-Deployment Checks (2-5 minutes)
- Wait for test suite to complete
- Verify all tests pass
- Block deployment if tests fail

#### Stage 2: Backend Deployment (3-5 minutes)
- Trigger Render deployment
- Wait for deployment to complete
- Run health checks
- Verify dependencies

#### Stage 3: Frontend Deployment (3-5 minutes)
- Build Next.js application
- Deploy to Vercel
- Run health checks
- Verify backend connectivity

#### Stage 4: Post-Deployment (1-2 minutes)
- End-to-end verification
- Generate deployment summary
- Send notifications

**Total Time:** ~10-15 minutes

### Monitoring Deployment Progress

#### GitHub Actions UI

1. Go to repository → Actions tab
2. Click on running workflow
3. View real-time logs for each job
4. Check deployment summary at bottom

#### Command Line

```bash
# Watch workflow runs
gh run watch

# List recent runs
gh run list --workflow=deploy.yml

# View specific run
gh run view <run-id>
```

#### Deployment Logs

**Backend (Render):**
```bash
# View logs in Render dashboard
# Or use Render CLI
render logs -s studyquest-backend
```

**Frontend (Vercel):**
```bash
# View logs in Vercel dashboard
# Or use Vercel CLI
vercel logs studyquest-frontend
```

## Rollback Procedures

### Automatic Rollback

The deployment workflow includes automatic rollback triggers:

**Backend Rollback Triggers:**
- Basic health check fails (10 attempts)
- Detailed health check fails
- Supabase dependency unhealthy
- OpenRouter dependency unhealthy

**Frontend Rollback Triggers:**
- Frontend health check fails
- Backend connectivity check fails
- Smoke tests fail (homepage or login)

### Manual Rollback

#### Backend (Render)

**Option 1: Render Dashboard**
1. Go to Render Dashboard
2. Select studyquest-backend service
3. Click "Manual Deploy" tab
4. Find previous successful deployment
5. Click "Redeploy"

**Option 2: Git Revert**
```bash
# Find the commit to revert to
git log --oneline

# Revert to previous commit
git revert <commit-hash>

# Push to trigger new deployment
git push origin main
```

#### Frontend (Vercel)

**Option 1: Vercel Dashboard**
1. Go to Vercel Dashboard
2. Select studyquest-frontend project
3. Go to Deployments tab
4. Find previous successful deployment
5. Click "..." → "Promote to Production"

**Option 2: Vercel CLI**
```bash
# List deployments
vercel ls studyquest-frontend

# Promote previous deployment
vercel promote <deployment-url> --scope=<team-name>
```

**Option 3: Git Revert**
```bash
# Revert to previous commit
git revert <commit-hash>
git push origin main
```

### Emergency Rollback

If automated systems fail:

1. **Disable Auto-Deploy:**
   ```bash
   # Temporarily disable workflow
   # Edit .github/workflows/deploy.yml
   # Change trigger to: workflow_dispatch only
   ```

2. **Manual Intervention:**
   - Use platform dashboards (Render/Vercel)
   - Redeploy last known good version
   - Fix issues in separate branch
   - Re-enable auto-deploy after fix

3. **Database Rollback:**
   ```bash
   # If database migrations were applied
   # Connect to Supabase
   # Run rollback migrations manually
   ```

### Rollback Checklist

After rollback:
- [ ] Verify services are healthy
- [ ] Check health endpoints
- [ ] Test critical user flows
- [ ] Monitor error rates
- [ ] Review logs for issues
- [ ] Document rollback reason
- [ ] Create fix in separate branch
- [ ] Test fix thoroughly before redeploying

## Monitoring Deployments

### Health Check Endpoints

Monitor deployment health:

```bash
# Backend basic health
curl https://your-backend.onrender.com/health

# Backend detailed health
curl https://your-backend.onrender.com/health/detailed

# Frontend health
curl https://your-frontend.vercel.app/api/health
```

### GitHub Actions Notifications

Configure notifications:

1. **Email Notifications:**
   - GitHub → Settings → Notifications
   - Enable "Actions" notifications

2. **Slack Integration:**
   ```yaml
   # Add to workflow
   - name: Notify Slack
     uses: 8398a7/action-slack@v3
     with:
       status: ${{ job.status }}
       webhook_url: ${{ secrets.SLACK_WEBHOOK }}
   ```

3. **Discord Integration:**
   ```yaml
   - name: Notify Discord
     uses: sarisia/actions-status-discord@v1
     with:
       webhook: ${{ secrets.DISCORD_WEBHOOK }}
   ```

### Deployment Metrics

Track key metrics:

- **Deployment Frequency**: How often you deploy
- **Lead Time**: Time from commit to production
- **Mean Time to Recovery (MTTR)**: Time to recover from failures
- **Change Failure Rate**: Percentage of deployments that fail

View in GitHub:
- Actions tab → Workflow runs
- Insights tab → Dependency graph → Deployments

## Troubleshooting

### Common Issues

#### 1. Tests Failing in CI but Passing Locally

**Symptoms:**
- Tests pass on local machine
- Tests fail in GitHub Actions

**Solutions:**

```bash
# Check environment differences
# Ensure secrets are configured in GitHub

# Run tests with same environment as CI
cd backend
SUPABASE_URL=<test-url> SUPABASE_KEY=<test-key> pytest

# Check Python/Node versions match
python --version  # Should be 3.11
node --version    # Should be 18
```

#### 2. Deployment Hangs or Times Out

**Symptoms:**
- Deployment workflow runs for >30 minutes
- No progress in logs

**Solutions:**

```bash
# Cancel workflow
gh run cancel <run-id>

# Check platform status
# Render: https://status.render.com
# Vercel: https://www.vercel-status.com

# Retry deployment
gh workflow run deploy.yml
```

#### 3. Health Checks Failing

**Symptoms:**
- Deployment completes but health checks fail
- Services show as unhealthy

**Solutions:**

```bash
# Check service logs
render logs -s studyquest-backend
vercel logs studyquest-frontend

# Verify environment variables
# Render Dashboard → Environment
# Vercel Dashboard → Settings → Environment Variables

# Test health endpoints manually
curl -v https://your-backend.onrender.com/health/detailed

# Check dependency status
# Verify Supabase is accessible
# Verify OpenRouter API key is valid
```

#### 4. Secrets Not Available

**Symptoms:**
- Workflow fails with "secret not found"
- Environment variables undefined

**Solutions:**

```bash
# Verify secrets are added
gh secret list

# Check secret names match workflow
# Secrets are case-sensitive

# Re-add secret if needed
gh secret set SUPABASE_URL

# For environment-specific secrets
# Ensure environment is specified in workflow
```

#### 5. Build Failures

**Symptoms:**
- Build step fails in workflow
- Dependency installation errors

**Solutions:**

```bash
# Clear cache and retry
# Edit workflow to add:
# cache: false

# Check dependency versions
# Ensure package.json and requirements.txt are up to date

# Test build locally
cd frontend
npm run build

cd backend
pip install -r requirements.txt
```

#### 6. Vercel Deployment Fails

**Symptoms:**
- Vercel deployment step fails
- "Invalid token" or "Project not found" errors

**Solutions:**

```bash
# Verify Vercel token
vercel whoami

# Re-link project
cd frontend
vercel link

# Check Vercel project settings
# Ensure build settings are correct

# Regenerate token if needed
# Vercel Dashboard → Settings → Tokens
```

#### 7. Render Deployment Fails

**Symptoms:**
- Render webhook returns error
- Service doesn't start

**Solutions:**

```bash
# Check Render service logs
render logs -s studyquest-backend

# Verify deploy hook URL
# Should be: https://api.render.com/deploy/...

# Check service status
# Render Dashboard → studyquest-backend

# Verify environment variables
# Ensure all required vars are set

# Manual deploy from dashboard
# Render Dashboard → Manual Deploy
```

### Debug Mode

Enable debug logging in workflows:

```yaml
# Add to workflow file
env:
  ACTIONS_STEP_DEBUG: true
  ACTIONS_RUNNER_DEBUG: true
```

### Getting Help

1. **Check workflow logs**: Actions tab → Failed workflow → View logs
2. **Review platform status**: Render/Vercel status pages
3. **Test locally**: Reproduce issue on local machine
4. **Check documentation**: Platform-specific docs
5. **Open issue**: GitHub repository issues

## Best Practices

### 1. Always Use Feature Branches

```bash
# Never commit directly to main
git checkout -b feature/my-feature
# Make changes
git push origin feature/my-feature
# Create PR
```

### 2. Write Good Commit Messages

```bash
# Good
git commit -m "Add user authentication endpoint"

# Bad
git commit -m "fix stuff"
```

### 3. Test Before Merging

- Run tests locally
- Verify CI passes on PR
- Review code changes
- Test in staging if available

### 4. Monitor Deployments

- Watch deployment progress
- Check health endpoints after deploy
- Monitor error rates
- Review logs for issues

### 5. Keep Secrets Secure

- Never commit secrets to code
- Rotate secrets regularly
- Use environment-specific secrets
- Limit secret access

### 6. Document Changes

- Update CHANGELOG
- Document breaking changes
- Update API documentation
- Notify team of deployments

## Next Steps

- Review [Docker Deployment Guide](./DOCKER_DEPLOYMENT.md) for containerized deployments
- Check [Operations Runbook](./OPERATIONS_RUNBOOK.md) for monitoring and maintenance
- See [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md) for detailed production setup

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
