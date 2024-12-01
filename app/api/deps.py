from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist  # Using consistent model name
from datetime import datetime

# Define the OAuth2 scheme with the correct signin endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/signin")


async def validate_token(token: str, db: Session) -> bool:
    """
    Check if a token is valid (not blacklisted and not expired).

    Args:
        token (str): The JWT token to validate
        db (Session): Database session for checking blacklist

    Returns:
        bool: True if token is valid, False if blacklisted
    """
    blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token,
        TokenBlacklist.expires_at > datetime.utcnow()
    ).first()

    # Return True if token is not blacklisted
    return not blacklisted


async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate JWT token, check blacklist, and return the current user.

    This function performs several security checks:
    1. Validates the token isn't blacklisted
    2. Verifies the JWT signature and decoding
    3. Ensures the user still exists in the database

    Args:
        db (Session): Database session dependency
        token (str): JWT token from request header

    Returns:
        User: The current authenticated user

    Raises:
        HTTPException: If any validation step fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # First check if token is blacklisted using our validate_token function
        if not await validate_token(token, db):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been invalidated. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # If token is valid, decode and verify it
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Extract user email from token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        # Get user from database
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception

        return user

    except JWTError:
        # Catches any JWT-specific errors (invalid signature, expired, etc.)
        raise credentials_exception