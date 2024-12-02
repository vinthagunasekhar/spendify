from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import get_db
from app.models.user import User
from app.models.token_blacklist import TokenBlacklist
from app.schemas.user import (
    UserSignInRequest,
    UserSignInResponse,
    UserSignupRequest,
    UserSignUpResponse,
    SignOutResponse,
    UserResponse,
    Token
)
from app.schemas.base import ErrorResponseSchema
from app.core.security import create_access_token
from fastapi.responses import JSONResponse
from datetime import datetime
import jwt.exceptions  # Import specific exceptions from PyJWT
from app.core.config import settings
import logging

# Set up logging for the authentication module
#logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Define OAuth2 scheme for token handling
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/signin")


async def validate_user_data(db: Session, email: str, user_name: str) -> Dict[str, str]:
    """
    Validate user data to ensure no duplicate entries.

    Args:
        db: Database session
        email: User's email to check
        user_name: Username to check

    Returns:
        Dict containing any validation errors found
    """
    errors: Dict[str, str] = {}

    try:
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            errors["email"] = "This email is already registered. Please login instead."

    except Exception as e:
        logger.error(f"Error during user validation: {str(e)}")
        errors["database"] = "Error checking user existence"

    return errors


@router.post(
    "/signup",
    response_model=UserSignUpResponse,
    responses={
        400: {"model": ErrorResponseSchema},
        409: {"model": ErrorResponseSchema}
    },
    summary="User Signup",
    description="Register a new user with spendify service"
)
async def signup(
        user_data: UserSignupRequest,
        db: Session = Depends(get_db)
) -> UserSignUpResponse:
    """Handle user registration process"""
    try:
        # Validate user data
        validation_errors = await validate_user_data(db, user_data.email, user_data.user_name)
        if validation_errors:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "status": "error",
                    "message": "Validation failed",
                    "details": validation_errors
                }
            )

        # Create new user
        new_user = User(email=user_data.email, user_name=user_data.user_name)
        new_user.set_password(user_data.password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserSignUpResponse(
            status="success",
            message="User registered successfully",
            data=UserResponse(
                id=new_user.id,
                email=new_user.email,
                user_name=new_user.user_name,
                created_at=new_user.created_at,
                updated_at=new_user.updated_at
            )
        )

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Database integrity error occurred",
                "details": str(e)
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "An error occurred while creating user",
                "details": str(e)
            }
        )


@router.post(
    "/signin",
    response_model=UserSignInResponse,
    responses={
        401: {"model": ErrorResponseSchema},
        400: {"model": ErrorResponseSchema}
    },
    summary="User Sign In",
    description="Authenticate a user and return a JWT token"
)
async def signin(
        user_data: UserSignInRequest,
        db: Session = Depends(get_db)
) -> UserSignInResponse:
    """Handle user authentication and token generation"""
    try:
        # Check if user exists
        user = db.query(User).filter(User.email == user_data.email).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Oh no! We did a thorough search in our DB but couldn't find this email. Maybe you forgot to signup first! Go to signup page :)",
                    "details": None
                }
            )

        # Verify password
        if not user.verify_password(user_data.password):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Hmm... the password doesn't match what we have in our DB. Please do a binary search in your memory! 🔍",
                    "details": None
                }
            )

        # Generate access token
        access_token = create_access_token(data={"sub": user.email})

        return UserSignInResponse(
            status="success",
            message="Welcome back! You've successfully signed in",
            data=Token(
                access_token=access_token,
                token_type="bearer"
            )
        )

    except Exception as e:
        logger.error(f"Error during signin: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "An unexpected error occurred during signin",
                "details": str(e)
            }
        )


@router.post(
    "/signout",
    response_model=SignOutResponse,
    responses={
        401: {"model": ErrorResponseSchema},
        400: {"model": ErrorResponseSchema}
    },
    summary="User Sign Out",
    description="Invalidate the current user's JWT token"
)
async def signout(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> SignOutResponse:
    """Handle user signout by blacklisting their token"""
    try:
        # Decode and verify the token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_email = payload.get("sub")

        # Verify user exists
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "status": "error",
                    "message": "Invalid token - user not found",
                    "details": None
                }
            )

        # Get token expiration time
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            raise jwt.exceptions.InvalidTokenError("Token has no expiration")

        expires_at = datetime.fromtimestamp(exp_timestamp)

        # Blacklist the token
        blacklist_entry = BlacklistedToken(
            token=token,
            expires_at=expires_at,
            blacklisted_by=user_email
        )

        db.add(blacklist_entry)
        db.commit()

        return SignOutResponse(
            status="success",
            message="You've successfully signed out. See you again soon! 👋",
            data=None
        )

    except jwt.exceptions.InvalidTokenError as e:
        logger.error(f"Invalid token during signout: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "status": "error",
                "message": "Invalid authentication token",
                "details": str(e)
            }
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error during signout: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": "An unexpected error occurred during signout",
                "details": str(e)
            }
        )