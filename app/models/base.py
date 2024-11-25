# app/models/base.py
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class BaseModel(Base):
    """
    Base model for other database models to inherit from.
    Provides common columns:
    - id: Primary key
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    """
    __abstract__ = True  # Tells SQLAlchemy not to create a table for this model

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Sets default to current timestamp
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Sets initial value
        onupdate=func.now(),  # Updates timestamp on each update
        nullable=False
    )