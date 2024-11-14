# app/core/config.py
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Base API Config
    PROJECT_NAME: str = "Spendify"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # CORS Origins for React Frontend
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React default port
        "http://localhost:5173",  # Vite default port
    ]

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()