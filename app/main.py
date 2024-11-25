# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Spendify API"
)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Spendify API",
        "database_url": settings.DATABASE_URL[:20] + "..."  # Show only start of URL for security
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "project_name": settings.PROJECT_NAME,
        "debug_mode": settings.DEBUG
    }