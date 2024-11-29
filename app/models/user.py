from sqlalchemy import Column, String
from app.models.base import BaseModel
import hashlib
import os
from sqlalchemy.orm import relationship


class User(BaseModel):
    """
    User model for storing user details.
    """
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    user_name = Column(String(50), nullable=False)
    salt= Column(String(32), nullable= False)

    # Relationships will be populated when the related models are loaded
    credit_cards = relationship(
        "CreditCard",
        back_populates="user",
        lazy="dynamic"
    )

    optimisations = relationship(
        "Optimisation",
        back_populates="user",
        lazy="dynamic"
    )

    def set_password(self, password: str):
        self.salt=os.urandom(16).hex()
        salted_password= (password + self.salt).encode('utf-8')
        self.hashed_password = hashlib.sha256(salted_password).hexdigest()

    def verify_password(self, password: str)-> bool:
        salted_password= (password + self.salt).encode('utf-8')
        return self.hashed_password == hashlib.sha256(salted_password).hexdigest()

    def __repr__(self):
        return f"<User {self.email}>"