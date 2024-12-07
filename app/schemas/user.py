from pydantic import BaseModel, EmailStr,constr, field_validator
from app.schemas.base import BaseSchema, ResponseSchema
from typing import Optional
from datetime import datetime

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str
    user_name: constr(min_length=3, max_length=10,pattern=r"^[a-zA-Z0-9_-]+$")

    @field_validator('password')
    @classmethod
    def password_validation(cls, password: str)->str:
        """
        Validate password meets security requirements:
        - At least 8 characters
        - Contains at least one letter
        - Contains at least one number
        """
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(c.isalpha() for c in password):
            raise ValueError("Password must contain at least one letter")

        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number")

        return password


class UserResponse(BaseSchema):
    email: str
    user_name: str

class UserSignUpResponse(ResponseSchema[UserResponse]):
    pass
class UserSignInRequest(BaseModel):
    """
    Schema for user sign in request.
    Only requires email and password.
    """
    email: EmailStr
    password: str

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "password": "yourpassword123"
            }
        }
    }

class Token(BaseModel):
    """
    Schema for JWT token response.
    Includes both access token and token type.
    """
    access_token: str
    token_type: str = "Bearer"  # token type is always Bearer


class UserSignInResponse(ResponseSchema[Token]):
    """
    Schema for successful user signin response.
    Wraps the token schema in our standard response format.
    """
    pass

class SignOutResponse(ResponseSchema):
    """
    Response schema for sign out endpoint.
    Inherits from base ResponseSchema for consistency.
    """
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "You've successfully signed out. See you again soon! 👋",
                "data": None
            }
        }