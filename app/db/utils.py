# app/db/utils.py
from sqlalchemy import text
from app.db.session import engine  # Use absolute import instead of relative

async def test_connection():
    try:
        # Try to connect and execute simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False