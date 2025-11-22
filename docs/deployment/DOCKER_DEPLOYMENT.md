# Docker Deployment Guide

This guide covers deploying StudyQuest using Docker containers for both local development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building Docker Images](#building-docker-images)
- [Running with Docker Compose](#running-with-docker-compose)
- [Environment Configuration](#environment-configuration)
- [Production Deployment](#production-deployment)
- [Health Checks](#health-checks)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker**: Version 20.10 or higher
  - Install: https://docs.docker.com/get-docker/
- **Docker Compose**: Version 2.0 or higher
  - Usually included with Docker Desktop
- **Git**: For cloning the repository

Verify installations:
```bash
docker --version
docker-compose --version
```

## Quick Start

Get up and running in 3 steps:

```bash
# 1. Clone the repository
git clone <repository-url>
cd studyquest

# 2. Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local
# Edit both files with your actual values

# 3. Start all services
docker-compose up -d
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Building Docker Images

### Backend Image

The backend uses a multi-stage build for optimal size and security:

```bash
# Build the backend image
cd backend
docker build -t studyquest-backend:latest .

# Build with custom tag
docker build -t studyquest-backend:v1.0.0 .
```

**Dockerfile Features:**
- **Multi-stage build**: Separates build and runtime dependencies
- **Non-root user**: Runs as `appuser` (UID 1000) for security
- **Minimal base**: Uses `python:3.11-slim` for smaller image size
- **Health checks**: Built-in health monitoring
- **Optimized layers**: Efficient caching for faster rebuilds

### Frontend Image

The frontend uses Next.js standalone output for minimal production size:

```bash
# Build the frontend image
cd frontend
docker build -t studyquest-frontend:latest .

# Build with custom tag
docker build -t studyquest-frontend:v1.0.0 .
```

**Dockerfile Features:**
- **Three-stage build**: Dependencies → Build → Production
- **Standalone output**: Minimal Next.js runtime
- **Non-root user**: Runs as `nextjs` (UID 1001)
- **Alpine base**: Ultra-small image size (~150MB)
- **Health checks**: Automatic health monitoring

### Build Arguments

You can pass build arguments for customization:

```bash
# Backend with custom Python version
docker build --build-arg PYTHON_VERSION=3.11 -t studyquest-backend .

# Frontend with custom Node version
docker build --build-arg NODE_VERSION=18 -t studyquest-frontend .
```

## Running with Docker Compose

Docker Compose orchestrates both services with proper networking and dependencies.

### Start Services

```bash
# Start in detached mode (background)
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d backend
```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View last 100 lines
docker-compose logs --tail=100
```

### Stop Services

```bash
# Stop all services (containers remain)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Stop and remove containers + images
docker-compose down --rmi all
```

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Rebuild and Restart

```bash
# Rebuild images and restart
docker-compose up -d --build

# Force rebuild (no cache)
docker-compose build --no-cache
docker-compose up -d
```

## Environment Configuration

### Backend Environment Variables

Create `backend/.env` from the example:

```bash
cp backend/.env.example backend/.env
```

**Required Variables:**

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# OpenRouter AI Configuration
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Security
JWT_SECRET=your_supabase_jwt_secret_here
ALLOWED_ORIGINS=http://localhost:3000

# Database Connection Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=5
DB_POOL_TIMEOUT=30
```

**Optional Variables:**

```bash
# Application
ENVIRONMENT=production
PORT=8000
LOG_LEVEL=info

# Service Role (admin operations only)
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
```

### Frontend Environment Variables

Create `frontend/.env.local` from the example:

```bash
cp frontend/.env.local.example frontend/.env.local
```

**Required Variables:**

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production Variables:**

```bash
# Use your deployed backend URL
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Docker Compose Environment

The `docker-compose.yml` automatically loads environment files:

- Backend: `./backend/.env`
- Frontend: `./frontend/.env.local`

You can override variables in `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - LOG_LEVEL=debug
      - DB_POOL_SIZE=20
```

## Production Deployment

### Resource Limits

The docker-compose configuration includes production-ready resource limits:

**Backend:**
- CPU: 1.0 core (limit), 0.5 core (reservation)
- Memory: 512MB (limit), 256MB (reservation)

**Frontend:**
- CPU: 0.5 core (limit), 0.25 core (reservation)
- Memory: 256MB (limit), 128MB (reservation)

### Restart Policies

Both services use `restart: on-failure:3`:
- Automatically restart on failure
- Maximum 3 restart attempts
- Prevents infinite restart loops

### Health Checks

Built-in health checks monitor service availability:

**Backend Health Check:**
```bash
# Runs every 30 seconds
curl http://localhost:8000/health
```

**Frontend Health Check:**
```bash
# Runs every 30 seconds
curl http://localhost:3000/api/health
```

### Production Checklist

Before deploying to production:

- [ ] Update environment variables with production values
- [ ] Set `ENVIRONMENT=production` in backend
- [ ] Update `ALLOWED_ORIGINS` with production domain
- [ ] Use production Supabase project
- [ ] Configure proper logging (structured JSON)
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Test health check endpoints
- [ ] Review resource limits
- [ ] Enable HTTPS/TLS
- [ ] Set up reverse proxy (nginx/Caddy)

### Deploying to Cloud Platforms

#### Railway (Backend)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway up
```

#### Vercel (Frontend)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy frontend
cd frontend
vercel --prod
```

#### Docker Registry

Push images to a registry for deployment:

```bash
# Tag images
docker tag studyquest-backend:latest your-registry/studyquest-backend:latest
docker tag studyquest-frontend:latest your-registry/studyquest-frontend:latest

# Push to registry
docker push your-registry/studyquest-backend:latest
docker push your-registry/studyquest-frontend:latest
```

## Health Checks

### Checking Service Health

**Basic Health Check:**
```bash
# Backend
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-22T10:30:00.000Z"
# }
```

**Detailed Health Check:**
```bash
# Backend with dependency status
curl http://localhost:8000/health/detailed

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-11-22T10:30:00.000Z",
#   "dependencies": {
#     "supabase": {
#       "status": "healthy",
#       "response_time_ms": 45
#     },
#     "openrouter": {
#       "status": "healthy"
#     }
#   }
# }
```

**Frontend Health Check:**
```bash
curl http://localhost:3000/api/health

# Response:
# {
#   "status": "healthy",
#   "backend": "connected",
#   "supabase": "connected"
# }
```

### Docker Health Status

Check container health status:

```bash
# View health status
docker ps

# Inspect health check details
docker inspect studyquest-backend | grep -A 10 Health
docker inspect studyquest-frontend | grep -A 10 Health
```

## Troubleshooting

### Common Issues

#### 1. Containers Won't Start

**Symptom:** `docker-compose up` fails or containers exit immediately

**Solutions:**

```bash
# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Verify environment variables
docker-compose config

# Check if ports are already in use
lsof -i :3000
lsof -i :8000

# Remove old containers and try again
docker-compose down
docker-compose up -d
```

#### 2. Environment Variables Not Loading

**Symptom:** Application can't connect to Supabase or OpenRouter

**Solutions:**

```bash
# Verify .env files exist
ls -la backend/.env
ls -la frontend/.env.local

# Check if variables are loaded
docker-compose exec backend env | grep SUPABASE
docker-compose exec frontend env | grep NEXT_PUBLIC

# Rebuild with no cache
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Frontend Can't Connect to Backend

**Symptom:** API calls fail with CORS or connection errors

**Solutions:**

```bash
# Check backend is running
curl http://localhost:8000/health

# Verify ALLOWED_ORIGINS in backend/.env
# Should include: http://localhost:3000

# Check docker network
docker network inspect studyquest_studyquest-network

# Restart both services
docker-compose restart
```

#### 4. Database Connection Errors

**Symptom:** Backend logs show Supabase connection failures

**Solutions:**

```bash
# Verify Supabase credentials
# Check SUPABASE_URL and SUPABASE_KEY in backend/.env

# Test connection manually
docker-compose exec backend python -c "
from config.supabase_client import get_supabase_client
client = get_supabase_client()
print(client.table('users').select('user_id').limit(1).execute())
"

# Check connection pool settings
# Increase DB_POOL_SIZE if needed
```

#### 5. Out of Memory Errors

**Symptom:** Containers crash with OOM (Out of Memory) errors

**Solutions:**

```bash
# Check memory usage
docker stats

# Increase memory limits in docker-compose.yml
# Backend: 512M → 1G
# Frontend: 256M → 512M

# Restart with new limits
docker-compose down
docker-compose up -d
```

#### 6. Build Failures

**Symptom:** `docker build` or `docker-compose build` fails

**Solutions:**

```bash
# Clear Docker cache
docker builder prune -a

# Build with verbose output
docker-compose build --progress=plain

# Check Dockerfile syntax
docker build --no-cache -t test-build ./backend

# Verify dependencies
# Backend: Check requirements.txt
# Frontend: Check package.json
```

#### 7. Health Checks Failing

**Symptom:** Containers show "unhealthy" status

**Solutions:**

```bash
# Check health check logs
docker inspect studyquest-backend --format='{{json .State.Health}}'

# Test health endpoint manually
docker-compose exec backend curl http://localhost:8000/health

# Increase health check timeout in docker-compose.yml
# timeout: 10s → 30s

# Check if application is actually running
docker-compose exec backend ps aux
```

### Debug Mode

Run containers in debug mode for troubleshooting:

```bash
# Run backend with shell access
docker-compose run --rm backend /bin/bash

# Run frontend with shell access
docker-compose run --rm frontend /bin/sh

# Execute commands in running container
docker-compose exec backend python --version
docker-compose exec frontend node --version
```

### Logs and Monitoring

```bash
# View structured logs (JSON format)
docker-compose logs backend | jq .

# Monitor resource usage
docker stats studyquest-backend studyquest-frontend

# Export logs to file
docker-compose logs > logs.txt

# Follow logs with timestamps
docker-compose logs -f -t
```

### Clean Slate

If all else fails, start fresh:

```bash
# Stop everything
docker-compose down -v

# Remove all StudyQuest images
docker rmi studyquest-backend studyquest-frontend

# Remove dangling images
docker image prune -a

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## Performance Optimization

### Image Size Optimization

Current image sizes:
- Backend: ~200MB (Python slim)
- Frontend: ~150MB (Node Alpine)

Tips for further optimization:
- Use `.dockerignore` to exclude unnecessary files
- Minimize layers in Dockerfile
- Use multi-stage builds (already implemented)
- Clean up package manager cache

### Build Speed Optimization

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build

# Cache dependencies separately
# Already implemented in multi-stage builds

# Parallel builds
docker-compose build --parallel
```

### Runtime Optimization

- Adjust resource limits based on actual usage
- Monitor with `docker stats`
- Use connection pooling (already configured)
- Enable response caching in application

## Security Best Practices

✅ **Already Implemented:**
- Non-root users in containers
- Multi-stage builds (minimal attack surface)
- Health checks for monitoring
- Resource limits to prevent DoS
- Environment variable isolation

🔒 **Additional Recommendations:**
- Use Docker secrets for sensitive data
- Scan images for vulnerabilities: `docker scan studyquest-backend`
- Keep base images updated
- Use specific image tags (not `latest`)
- Enable Docker Content Trust
- Run containers in read-only mode where possible

## Next Steps

- Review [CI/CD Guide](./CICD_GUIDE.md) for automated deployments
- Check [Operations Runbook](./OPERATIONS_RUNBOOK.md) for monitoring
- See [Production Deployment Guide](./PRODUCTION_DEPLOYMENT_GUIDE.md) for cloud deployment

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review health checks: `curl http://localhost:8000/health/detailed`
- Consult troubleshooting section above
- Open an issue on GitHub
