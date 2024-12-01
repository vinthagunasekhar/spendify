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

    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "10.183.88.243")  # Your GCP Redis instance host
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_AUTH_ENABLED: bool = True
    REDIS_AUTH_STRING: str = os.getenv("REDIS_AUTH_STRING", "782859a0-15b6-4080-bd06-5ff305679cf9")

    # Network settings
    REDIS_NETWORK: str = "default (spendify-441605)"
    REDIS_IP_RANGE: str = "10.183.88.240/29"

    # Redis Connection Settings
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_TIMEOUT: int = 5  # seconds
    REDIS_RETRY_TIMES: int = 3
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()