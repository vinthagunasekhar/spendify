# app/api/deps.py
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Add your user authentication logic here
    # This is a placeholder
    return {"username": "test_user"}