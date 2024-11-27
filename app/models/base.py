from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from app.db.base_class import Base  # Changed this line

class BaseModel(Base):
    """
    Base model for other database models to inherit from.
    Think of this as a template for all our database tables.
    Every table will automatically get:
    - An ID column that auto-increments
    - A creation timestamp
    - An update timestamp that changes automatically
    """
    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # When a record is created, set to current time
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Initially set to creation time
        onupdate=func.now(),     # Automatically updates when record changes
        nullable=False
    )