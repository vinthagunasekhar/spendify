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