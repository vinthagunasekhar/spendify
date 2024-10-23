from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class CreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_name = db.Column(db.String(100), nullable=False)
    credit_limit = db.Column(db.Float, nullable=False)
    cycle_start = db.Column(db.Integer, nullable=False)  # Day of month
    cycle_end = db.Column(db.Integer, nullable=False)    # Day of month
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cards = db.relationship('CreditCard', backref='user', lazy=True)
