from app.models.base import BaseModel
from app.models.user import User
from app.models.credit_card import CreditCard
from app.models.optimisation import Optimisation
from app.models.token_blacklist import TokenBlacklist

# This file ensures proper model registration order
# All models should be imported here to be included in migrations

__all__ = [
    'BaseModel',
    'User',
    'CreditCard',
    'Optimisation',
    'blacklisted_tokens'
]