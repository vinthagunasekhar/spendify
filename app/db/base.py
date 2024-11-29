# Import all models here for Alembic to discover them
from app.db.base_class import Base
from app.models.user import User
from app.models.credit_card import CreditCard
from app.models.optimisation import Optimisation