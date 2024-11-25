# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    # These parameters are important for PostgreSQL
    pool_pre_ping=True,  # Enables connection health checks
    pool_size=5,         # Number of connections to maintain
    max_overflow=10      # Max extra connections to allow
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,    # Transactions must be committed explicitly
    autoflush=False,     # Changes won't be automatically flushed
    bind=engine          # Bind to our database engine
)

# Create Base class for SQLAlchemy models
Base = declarative_base()

# Database dependency for FastAPI
def get_db():
    """
    Generator function that yields database sessions
    Used as a FastAPI dependency
    """
    db = SessionLocal()
    try:
        yield db  # Yields the database session
        # This session will be used in API endpoints
    finally:
        db.close()  # Ensures the session is closed after request