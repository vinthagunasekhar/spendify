
# CARD_NAMES = [
#     "CIBC",
#     "TD",
#     "RBC",
#     "Scotiabank",
#     "BMO",
#     "Capital One",
#     "American Express",
#     "PC Financial",
#     "Walmart"
# ]

from datetime import timedelta

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///credit_cards.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
