from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import Config

db = SQLAlchemy()


class CreditCard(db.Model):
    """Model for storing credit card information."""
    __tablename__ = 'credit_card'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_name = db.Column(db.String(50), nullable=False)
    credit_limit = db.Column(db.Float, nullable=False)
    billing_start_date = db.Column(db.Integer, nullable=False)
    billing_end_date = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model):
    """Model for storing user information."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cards = db.relationship('CreditCard', backref='user', lazy=True)