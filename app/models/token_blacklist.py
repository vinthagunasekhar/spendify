from sqlalchemy import Column, String, DateTime
from app.models.base import BaseModel
from datetime import datetime


class BlacklistedToken(BaseModel):
    """
    Model for storing invalidated JWT tokens in PostgreSQL.
    Each entry represents a token that has been invalidated through user logout.
    """
    __tablename__ = "blacklisted_tokens"

    # The token that has been invalidated
    token = Column(String(500), unique=True, nullable=False, index=True)

    # When this token expires (matches JWT expiration)
    expires_at = Column(DateTime, nullable=False, index=True)

    # Who blacklisted this token (usually the user's email)
    blacklisted_by = Column(String(255), nullable=False)

    @classmethod
    def is_blacklisted(cls, db_session, token: str) -> bool:
        """
        Check if a token is blacklisted and not expired.
        Returns True if the token is found in the blacklist and hasn't expired.
        """
        return db_session.query(cls).filter(
            cls.token == token,
            cls.expires_at > datetime.utcnow()
        ).first() is not None

    def __repr__(self):
        """String representation of the blacklisted token"""
        return f"<BlacklistedToken expires_at={self.expires_at}>"