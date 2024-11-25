from sqlalchemy import Column, Integer, ForeignKey, String, SmallInteger
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Optimisation(BaseModel):
    """
    Optimisation model for storing optimisation strategies for users.
    """
    __tablename__ = "optimisations"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_name = Column(String(50), nullable=False)
    value_start = Column(SmallInteger, nullable=False)
    value_end = Column(SmallInteger, nullable=False)

    user = relationship("User", back_populates="optimisations")

    def __repr__(self):
        return f"<Optimisation {self.card_name} {self.value_start}-{self.value_end}>"