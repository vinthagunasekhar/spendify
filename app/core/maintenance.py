# app/core/maintenance.py

from app.db.session import SessionLocal
from app.models.token_blacklist import TokenBlacklist
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def cleanup_expired_tokens():
    """
    Remove expired tokens from the blacklist table.
    Can be run as a scheduled task (e.g., daily cron job).
    """
    db = SessionLocal()
    try:
        # Delete all expired tokens
        deleted = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < datetime.utcnow()
        ).delete()

        db.commit()
        logger.info(f"Cleaned up {deleted} expired tokens from blacklist")

    except Exception as e:
        logger.error(f"Error during token cleanup: {str(e)}")
        db.rollback()

    finally:
        db.close()