# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import router as api_v1_router


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

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Spendify API",
        "version": "1.0.0",
        "database_url": settings.DATABASE_URL[:10] + "..."  # Show only start of URL for security
    }
