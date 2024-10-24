from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config

db = SQLAlchemy()


class CreditCard(db.Model):
    """Model for storing credit card information."""
    __tablename__ = 'credit_card'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_type = db.Column(db.String(50), nullable=False)  # Increased length for longer card names
    credit_limit = db.Column(db.Float, nullable=False)
    cycle_start = db.Column(db.Integer, nullable=False)
    cycle_end = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def card_name(self):
        return self.card_type  # Simply return the card type as it's already the full name


class User(db.Model):
    """Model for storing user information."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cards = db.relationship('CreditCard', backref='user', lazy=True)