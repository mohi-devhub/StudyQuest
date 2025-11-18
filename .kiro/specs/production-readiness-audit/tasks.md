# Implementation Plan

- [x] 1. Security Audit and Hardening
  - Scan codebase for security vulnerabilities and implement fixes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 1.1 Scan for hardcoded secrets and API keys
  - Create secret scanner utility that searches for API keys, passwords, tokens in source code
  - Scan all Python and TypeScript files using regex patterns
  - Generate report of findings with file paths and line numbers
  - _Requirements: 1.1_

- [x] 1.2 Run dependency vulnerability scans
  - Execute `npm audit` in frontend directory and parse JSON output
  - Execute `pip-audit` in backend directory (install if needed)
  - Categorize vulnerabilities by severity (critical, high, medium, low)
  - Generate prioritized list of vulnerable packages with CVE details
  - _Requirements: 1.2_

- [x] 1.3 Add JWT authentication to retry endpoint
  - Import authentication middleware in `backend/routes/study.py`
  - Add `current_user: dict = Depends(verify_user)` to retry endpoint
  - Replace hardcoded 'demo_user' with `current_user['user_id']`
  - Update endpoint to return 401 if authentication fails
  - _Requirements: 1.5_

- [x] 1.4 Implement rate limiting on AI endpoints
  - Add rate limiting decorator to `/coach/feedback/{user_id}` endpoint
  - Add rate limiting to `/study/retry` endpoint (5 requests per minute)
  - Add rate limiting to quiz generation endpoints
  - Configure rate limits: AI endpoints 5/min, regular endpoints 10/min
  - _Requirements: 6.4_

- [x] 1.5 Add input validation middleware
  - Create validation utility in `backend/utils/validation.py`
  - Add topic name validation (max length 200, alphanumeric + spaces)
  - Add user_id validation (UUID format)
  - Add request size limits (max 10KB for most endpoints)
  - _Requirements: 1.4_

- [x] 1.6 Update vulnerable dependencies
  - Update npm packages with high/critical vulnerabilities
  - Update pip packages with known CVEs
  - Test application after updates to ensure no breaking changes
  - _Requirements: 1.2_

- [x] 2. Docker Configuration
  - Create production-ready Docker configurations for containerized deployment
  - _Requirements: 2.1, 2.2_

- [x] 2.1 Create backend Dockerfile
  - Create `backend/Dockerfile` with multi-stage build
  - Stage 1: Install dependencies using python:3.11-slim
  - Stage 2: Production image with non-root user (appuser)
  - Copy only necessary files, set proper permissions
  - Expose port 8000, set CMD to run uvicorn
  - _Requirements: 2.1_

- [x] 2.2 Create frontend Dockerfile
  - Create `frontend/Dockerfile` with multi-stage build
  - Stage 1: Install dependencies using node:18-alpine
  - Stage 2: Build Next.js application
  - Stage 3: Production image with standalone output
  - Use non-root user, expose port 3000
  - _Requirements: 2.1_

- [x] 2.3 Create docker-compose.yml
  - Create `docker-compose.yml` in project root
  - Define services: backend, frontend
  - Configure environment variables from .env files
  - Set up networking between services
  - Add health checks for both services
  - _Requirements: 2.1_

- [x] 2.4 Create .dockerignore files
  - Create `backend/.dockerignore` (exclude venv, __pycache__, .env, tests)
  - Create `frontend/.dockerignore` (exclude node_modules, .next, .env.local)
  - _Requirements: 2.1_

- [x] 3. CI/CD Pipeline Implementation
  - Set up automated testing and deployment workflows
  - _Requirements: 2.4, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 3.1 Create GitHub Actions test workflow
  - Create `.github/workflows/test.yml`
  - Add job for backend tests (pytest, pip-audit)
  - Add job for frontend tests (lint, type-check, jest, npm audit)
  - Run on pull requests and pushes to main/develop
  - _Requirements: 7.1, 7.2_

- [x] 3.2 Create GitHub Actions deployment workflow
  - Create `.github/workflows/deploy.yml`
  - Add backend deployment job (Railway)
  - Add frontend deployment job (Vercel)
  - Run only on pushes to main branch
  - Require test workflow to pass first
  - _Requirements: 7.2, 7.3_

- [x] 3.3 Create GitHub Actions security scan workflow
  - Create `.github/workflows/security.yml`
  - Add dependency vulnerability scanning
  - Add secret scanning check
  - Run weekly and on pull requests
  - _Requirements: 7.2_

- [x] 3.4 Add deployment health check verification
  - Add post-deployment health check step to deployment workflow
  - Verify /health endpoint returns 200
  - Verify /health/detailed shows all dependencies healthy
  - Implement automatic rollback if health checks fail
  - _Requirements: 7.4_

- [x] 4. Structured Logging Implementation
  - Replace console.log and print statements with structured JSON logging
  - _Requirements: 3.1, 3.3_

- [x] 4.1 Create backend structured logger
  - Create `backend/utils/logger.py` with StructuredLogger class
  - Implement JSON formatter with timestamp, level, logger name, message, context
  - Add methods: info(), error(), warning(), debug()
  - Configure log level from environment variable
  - _Requirements: 3.1_

- [x] 4.2 Create frontend structured logger
  - Create `frontend/lib/logger.ts` with StructuredLogger class
  - Implement JSON logging with timestamp, level, message, context
  - Add production mode check (send to logging service vs console)
  - Add methods: info(), error(), warn(), debug()
  - _Requirements: 3.1_

- [x] 4.3 Replace backend print statements with logger
  - Import logger in all agent files (adaptive_quiz_agent.py, coach_agent.py, recommendation_agent.py)
  - Replace print() calls with logger.info() or logger.debug()
  - Add context to log messages (user_id, topic, model, etc.)
  - _Requirements: 3.1_

- [x] 4.4 Replace frontend console.log with logger
  - Import logger in all page components
  - Replace console.log with logger.info()
  - Replace console.error with logger.error()
  - Add context to log messages (user_id, page, action)
  - _Requirements: 3.1_

- [x] 5. Health Check Endpoints
  - Implement comprehensive health monitoring
  - _Requirements: 3.2, 3.3_

- [x] 5.1 Enhance health check endpoint with detailed status
  - Create `backend/routes/health.py` router with GET /health/detailed endpoint
  - Check Supabase connection (query users table with timing)
  - Check OpenRouter API availability with timeout
  - Return status for each dependency with response times
  - Set overall status to 'degraded' if any dependency fails
  - Mount router in main.py
  - _Requirements: 3.2_

- [x] 5.2 Add frontend health check
  - Create API route `frontend/app/api/health/route.ts`
  - Check backend API connectivity
  - Check Supabase client initialization
  - Return health status JSON
  - _Requirements: 3.2_

- [x] 6. Testing Enhancement
  - Improve test coverage for critical paths
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 6.1 Create authentication flow tests
  - Create `backend/tests/test_auth_flow.py`
  - Test protected endpoint without authentication (expect 401)
  - Test protected endpoint with valid JWT (expect 200)
  - Test protected endpoint with expired token (expect 401)
  - Test protected endpoint with invalid token (expect 401)
  - _Requirements: 4.1, 4.3_

- [x] 6.2 Create AI agent integration tests
  - Create `backend/tests/test_ai_agents_integration.py`
  - Test quiz generation with various difficulties
  - Test recommendation generation with user progress data
  - Test coach feedback generation
  - Verify response structure and quality
  - _Requirements: 4.1, 4.3_

- [x] 6.3 Create API endpoint integration tests
  - Create `backend/tests/test_api_endpoints.py`
  - Test /study/retry endpoint with authentication
  - Test /progress/v2/user/{user_id}/stats endpoint
  - Test /achievements/user/{user_id}/badges endpoint
  - Verify response codes and data structure
  - _Requirements: 4.3_

- [ ]* 6.4 Generate test coverage report
  - Run pytest with coverage: `pytest --cov=. --cov-report=html`
  - Generate coverage report in htmlcov/ directory
  - Identify untested code paths
  - _Requirements: 4.2_

- [x] 6.5 Create frontend component tests
  - Add tests for XPProgressBar component (already exists in __tests__)
  - Add tests for TopicCard component (already exists in __tests__)
  - Add tests for CoachFeedbackPanel component
  - Test rendering and user interactions
  - _Requirements: 4.1_

- [x] 7. Performance Optimization
  - Optimize database queries and resource usage
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7.1 Add database indexes for core tables
  - Create migration file `migrations/ADD_PERFORMANCE_INDEXES.sql`
  - Add index on user_topics(user_id) if not exists
  - Add composite index on quiz_scores(user_id, topic) if not exists
  - Add index on xp_history(user_id, created_at DESC) if not exists
  - Add index on user_badges(user_id, unlocked_at DESC) if not exists
  - Note: study_sessions already has indexes
  - _Requirements: 5.1_

- [x] 7.2 Implement connection pooling
  - Update `backend/config/supabase_client.py`
  - Add connection pool configuration (pool_size=10, max_overflow=5)
  - Add environment variables for pool settings (DB_POOL_SIZE, DB_MAX_OVERFLOW, DB_POOL_TIMEOUT)
  - Add connection timeout configuration
  - _Requirements: 5.2_

- [x] 7.3 Add resource limits to Docker configs
  - Update docker-compose.yml with memory limits (backend: 512MB, frontend: 256MB)
  - Add CPU limits (backend: 1.0, frontend: 0.5)
  - Update restart policy to: on-failure with max retries
  - _Requirements: 5.4_

- [ ]* 7.4 Profile and optimize slow queries
  - Enable query logging in Supabase dashboard
  - Identify queries taking >500ms using Supabase performance insights
  - Optimize query structure (add select specific columns, use joins)
  - Re-test query performance
  - _Requirements: 5.3_

- [x] 8. AI System Validation and Optimization
  - Validate AI model configurations and optimize costs
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8.1 Validate AI model selections
  - Review current model usage in adaptive_quiz_agent.py, recommendation_agent.py, coach_agent.py
  - Verify using google/gemini-2.0-flash-exp:free (optimal free model) - CONFIRMED
  - Document model selection rationale in code comments
  - Verify fallback models are configured - CONFIRMED (llama models as fallback)
  - _Requirements: 8.1_

- [x] 8.2 Test AI response quality
  - Create `backend/tests/test_ai_quality.py`
  - Test quiz generation produces valid questions (4 options, 1 answer)
  - Test recommendations are relevant to user progress
  - Test coach feedback is contextual and helpful
  - Verify response times are acceptable (<3 seconds)
  - _Requirements: 8.2_

- [x] 8.3 Implement AI response caching
  - Create `backend/utils/ai_cache.py` with AIResponseCache class
  - Implement cache key generation from prompt + model
  - Add TTL-based cache expiration (1 hour)
  - Integrate caching into quiz generation
  - Integrate caching into recommendation generation
  - Note: cache_utils.py exists but is for general content caching, not AI-specific
  - _Requirements: 8.3_

- [ ]* 8.4 Add AI cost tracking
  - Create `backend/utils/ai_metrics.py` for tracking AI usage
  - Log token usage for each AI request
  - Calculate estimated costs (even for free tier, track usage)
  - Add metrics endpoint GET /metrics/ai-usage
  - _Requirements: 8.3_

- [x] 8.5 Validate AI error handling
  - Test AI endpoints with invalid API key (should use fallback)
  - Test AI endpoints with network timeout (should return graceful error)
  - Test AI endpoints with rate limit exceeded (should retry with backoff)
  - Verify error messages are user-friendly
  - _Requirements: 8.4_

- [ ] 9. Documentation Updates
  - Update documentation with new configurations and deployment instructions
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 9.1 Create Docker deployment guide
  - Create `docs/DOCKER_DEPLOYMENT.md`
  - Document how to build Docker images
  - Document how to run with docker-compose
  - Include environment variable configuration
  - Add troubleshooting section
  - _Requirements: 9.3_

- [ ] 9.2 Create CI/CD documentation
  - Create `docs/CICD_GUIDE.md`
  - Document GitHub Actions workflows (test.yml, deploy.yml, security.yml)
  - Explain deployment process
  - Document how to configure secrets in GitHub
  - Add rollback procedures
  - _Requirements: 9.3_

- [ ] 9.3 Update main README
  - Add Docker deployment section
  - Add CI/CD pipeline status badges
  - Update architecture diagram with new components (health checks, structured logging)
  - Add health check endpoint documentation
  - Update troubleshooting section
  - _Requirements: 9.1, 9.2_

- [ ] 9.4 Create operations runbook
  - Create `docs/OPERATIONS_RUNBOOK.md`
  - Document how to check application health (/health, /health/detailed)
  - Document how to view structured logs
  - Document common issues and solutions
  - Add monitoring and alerting setup recommendations
  - _Requirements: 9.3_

- [ ] 9.5 Update API documentation
  - Update existing API docs with new endpoints (/health, /health/detailed)
  - Document rate limiting behavior (already implemented with SlowAPI)
  - Document authentication requirements
  - Add example requests and responses
  - _Requirements: 9.2_

- [ ] 10. Final Validation and Deployment
  - Validate all fixes and deploy to production
  - _Requirements: All_

- [ ]* 10.1 Run complete test suite
  - Execute backend tests: `cd backend && pytest`
  - Execute frontend tests: `cd frontend && npm test`
  - Verify all tests pass
  - Check test coverage meets 80% threshold
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 10.2 Build and test Docker images
  - Build backend Docker image: `docker build -t studyquest-backend ./backend`
  - Build frontend Docker image: `docker build -t studyquest-frontend ./frontend`
  - Run docker-compose up and verify services start
  - Test health check endpoints (basic /health and new /health/detailed)
  - _Requirements: 2.1_

- [ ] 10.3 Validate security fixes
  - Re-run secret scanner (should find no secrets)
  - Re-run dependency vulnerability scans (should have no critical/high)
  - Test authentication on protected endpoints
  - Verify rate limiting works (already implemented with SlowAPI)
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 10.4 Deploy to staging environment
  - Deploy backend to Railway staging
  - Deploy frontend to Vercel preview
  - Run smoke tests on staging
  - Verify health checks pass
  - Test critical user flows
  - _Requirements: 7.2, 7.4_

- [ ]* 10.5 Deploy to production
  - Merge to main branch (triggers CI/CD)
  - Monitor deployment logs
  - Verify health checks pass in production
  - Test critical endpoints
  - Monitor error rates and performance
  - _Requirements: 7.2, 7.4_

- [ ] 10.6 Create production readiness report
  - Generate final audit report with all fixes applied
  - Document remaining known issues (if any)
  - Create checklist for ongoing maintenance
  - Document monitoring and alerting setup
  - _Requirements: All_
