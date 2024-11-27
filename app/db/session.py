from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine with important PostgreSQL settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,     # Like checking if a phone line is alive before calling
    pool_size=5,            # Keep 5 database connections ready to use
    max_overflow=10         # Allow up to 10 extra connections when busy
)

# Create session factory - think of it as a template for database conversations
SessionLocal = sessionmaker(
    autocommit=False,    # Changes aren't saved until we explicitly commit
    autoflush=False,     # Changes aren't automatically synced with database
    bind=engine          # Connect this session maker to our database engine
)

def get_db():
    """
    Creates a new database session for each request and closes it afterward.
    It's like opening a new conversation with the database, using it,
    and making sure to end it properly when we're done.
    """
    db = SessionLocal()
    try:
        yield db  # Give the session to FastAPI to use
    finally:
        db.close()  # Always close the session, even if errors occur