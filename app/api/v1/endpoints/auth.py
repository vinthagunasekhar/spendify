from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserSignupRequest, UserSignUpResponse, UserResponse
from app.schemas.base import ErrorResponseSchema
from sqlalchemy.exc import IntegrityError
from typing import Dict

router = APIRouter()

async def validate_user_data(db: Session, email: str, user_name: str)->Dict[str,str]:
    """
    Validate user data to ensure no duplicate entries.
    """
    errors={}
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        errors["email"]="This email is already registered. Please login instead."

    return errors

@router.post("/signup",response_model=UserSignUpResponse,
             responses={400: {"model": ErrorResponseSchema}, 409: {"model": ErrorResponseSchema}},
             summary="User Signup",
             description="Register a new user with spendify service.")
async def signup(user_data: UserSignupRequest, db:Session= Depends(get_db)):
    validation_errors= await validate_user_data(db, user_data.email, user_data.user_name)
    if validation_errors:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"status":"error","message":"validation failed", "details": validation_errors})
    try:
        new_user= User(email=user_data.email, user_name=user_data.user_name)
        new_user.set_password(user_data.password)

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserSignUpResponse(status="success", message="User registered successfully", data=UserResponse(id=new_user.id, email=new_user.email, user_name=new_user.user_name, created_at=new_user.created_at, updated_at=new_user.updated_at))
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status":"error","message":"Database integrity error occured", "details": str(e)})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"status":"error","message":"An error occured while creating user", "details": str(e)})

