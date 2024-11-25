from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from sqlalchemy.sql import func

class CreditCard(BaseModel):
    """
    CreditCard model for storing credit card details.
    """
    __tablename__ = "credit_cards"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_name = Column(String(50), nullable=False)
    credit_limit = Column(Integer, nullable=False)
    billing_start_date = Column(SmallInteger, nullable=False)
    billing_end_date = Column(SmallInteger, nullable=False)

    user = relationship("User", back_populates="credit_cards")

    def __repr__(self):
        return f"<CreditCard {self.card_name}>"