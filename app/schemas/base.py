# app/schemas/base.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Generic, TypeVar, Any, Dict, List

T = TypeVar('T')  # Type variable for generic schemas


class BaseSchema(BaseModel):
    """
    Base Pydantic model for all schemas to inherit from.
    Includes common attributes like id and timestamps.
    """
    model_config = ConfigDict(from_attributes=True)  # Allows conversion from ORM models

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ResponseSchema(BaseModel, Generic[T]):
    """
    Standard response schema for API endpoints.
    Provides consistent response structure.
    """
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {}
            }
        }


class PaginatedResponseSchema(ResponseSchema[List[T]]):
    """
    Response schema for paginated results.
    Includes pagination metadata.
    """
    total: int
    page: int
    size: int
    pages: int
    data: List[T]


class ErrorResponseSchema(BaseModel):
    """
    Standard error response schema.
    Used for consistent error reporting.
    """
    status: str = "error"
    message: str
    details: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "error",
                "message": "An error occurred",
                "details": {
                    "field": "description of error"
                }
            }
        }