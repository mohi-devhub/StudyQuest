# GitHub Actions CI/CD Workflows

This directory contains automated workflows for testing, security scanning, and deployment.

## Workflows

### 1. Test Suite (`test.yml`)
**Triggers:** Push to main/develop, Pull Requests

**Jobs:**
- **Backend Tests**: Runs pytest with coverage, pip-audit security scan
- **Frontend Tests**: Runs linting, type checking, Jest tests, npm audit, and build verification

**Required Secrets:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GEMINI_API_KEY`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### 2. Deployment (`deploy.yml`)
**Triggers:** Push to main branch, Manual dispatch

**Jobs:**
1. **Check Tests**: Waits for test workflow to pass
2. **Deploy Backend**: Deploys to Railway with health checks
3. **Deploy Frontend**: Deploys to Vercel with health checks
4. **Post-Deployment Verification**: Comprehensive health verification
5. **Notify**: Reports deployment status

**Health Checks:**
- Basic health endpoint verification (200 status)
- Detailed health check with dependency status
- Supabase connectivity verification
- OpenRouter API availability check
- Frontend smoke tests (homepage, login page)
- Automatic rollback on failure

**Required Secrets:**
- `RAILWAY_TOKEN`
- `VERCEL_TOKEN`
- All secrets from test workflow

### 3. Security Scan (`security.yml`)
**Triggers:** Weekly (Mondays 9 AM UTC), Pull Requests, Manual dispatch

**Jobs:**
- **Dependency Scan**: pip-audit (backend), npm audit (frontend)
- **Secret Scan**: Custom scanner + TruffleHog
- **Code Security**: Bandit (Python), ESLint (TypeScript)
- **Security Summary**: Aggregates all scan results

**Artifacts Generated:**
- `backend-vulnerabilities.json`
- `frontend-vulnerabilities.json`
- `secret-scan-results`
- `bandit-security-report.json`
- `eslint-security-report.json`

## Setup Instructions

### 1. Configure GitHub Secrets

Go to your repository Settings → Secrets and variables → Actions, and add:

**Supabase:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

**OpenRouter:**
```
OPENROUTER_API_KEY=your-openrouter-key
```

**Railway:**
```
RAILWAY_TOKEN=your-railway-token
```

**Vercel:**
```
VERCEL_TOKEN=your-vercel-token
```

### 2. Railway Setup

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Link project: `railway link`
4. Get token: `railway whoami --token`

### 3. Vercel Setup

1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Link project: `vercel link`
4. Get token from: https://vercel.com/account/tokens

## Workflow Features

### Automatic Rollback
- Backend: Uses Railway's rollback command if health checks fail
- Frontend: Alerts for manual intervention (Vercel limitation)

### Health Check Verification
- Verifies `/health` endpoint returns 200
- Checks `/health/detailed` for dependency status
- Validates Supabase and OpenRouter connectivity
- Tests critical frontend pages

### Security Scanning
- Weekly automated scans
- Pull request security checks
- Multiple scanning tools (pip-audit, npm audit, Bandit, TruffleHog)
- Artifact uploads for detailed review

## Monitoring Deployment

### View Workflow Runs
Go to: Repository → Actions tab

### Check Deployment Status
- Green checkmark: Deployment successful
- Red X: Deployment failed (check logs)
- Yellow dot: Deployment in progress

### Review Health Checks
Click on a workflow run → Expand job → View health check steps

## Troubleshooting

### Tests Failing
1. Check test logs in Actions tab
2. Run tests locally: `cd backend && pytest` or `cd frontend && npm test`
3. Verify environment variables are set correctly

### Deployment Failing
1. Check health check logs
2. Verify Railway/Vercel tokens are valid
3. Check backend/frontend logs in respective platforms
4. Ensure all secrets are configured

### Security Scan Issues
1. Review artifact reports
2. Update vulnerable dependencies
3. Remove any detected secrets
4. Fix code security issues flagged by Bandit/ESLint

## Best Practices

1. **Always run tests locally** before pushing
2. **Review security scan results** weekly
3. **Monitor deployment health checks** after each release
4. **Keep dependencies updated** to avoid vulnerabilities
5. **Rotate secrets regularly** for security

## Next Steps

- [ ] Configure notification webhooks (Slack, Discord, etc.)
- [ ] Add performance monitoring integration
- [ ] Set up automated database migrations
- [ ] Configure blue-green deployment strategy
- [ ] Add load testing to deployment pipeline
