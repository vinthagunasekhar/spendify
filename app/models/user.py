from sqlalchemy import Column, String
from app.models.base import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import relationship

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    """
    User model for storing user details.
    """
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    user_name = Column(String(50), nullable=False)

    credit_cards= relationship("CreditCard", back_populates="user")
    optimisations = relationship("Optimisation", back_populates="user")

    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def __repr__(self):
        return f"<User {self.email}>"