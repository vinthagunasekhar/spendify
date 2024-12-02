from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): Payload to encode in the token
        expires_delta (Optional[timedelta]): Token expiration time.
                                           If None, uses default from settings

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()  # Create a copy of the data to avoid modifying the original

    # Set token expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiration time to token payload
    to_encode.update({"exp": expire})

    # Create JWT token using your secret key and algorithm
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token (str): JWT token to verify

    Returns:
        dict: Decoded token payload

    Raises:
        jwt.PyJWTError: If token is invalid
    """
    decoded_token = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    return decoded_token