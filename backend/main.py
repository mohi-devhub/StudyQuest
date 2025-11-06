from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routes import auth, study, quiz, progress, progress_v2

# Initialize FastAPI app
app = FastAPI(
    title="StudyQuest API",
    description="AI-powered study management platform backend",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
        "https://*.vercel.app",   # Vercel deployments
        # Add your custom domain here when ready
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(study.router)
app.include_router(quiz.router)
app.include_router(progress.router)
app.include_router(progress_v2.router)  # Enhanced progress tracking

# Root endpoint
@app.get("/")
async def root():
    return {"message": "StudyQuest Backend Running"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
