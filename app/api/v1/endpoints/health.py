# app/api/v1/endpoints/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.base import ResponseSchema

router = APIRouter()

@router.get(
    "",
    response_model=ResponseSchema,
    summary="Health Check",
    description="Check if the API and database are healthy"
)
async def health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute("SELECT 1")
        return ResponseSchema(
            status="success",
            message="System is healthy",
            data={
                "database": "connected",
                "api_version": "1.0"
            }
        )
    except Exception as e:
        return ResponseSchema(
            status="error",
            message="System health check failed",
            data={
                "database": "disconnected",
                "error": str(e)
            }
        )