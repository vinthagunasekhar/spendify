from flask import Flask
from models import db, User, CreditCard
from config import Config
import os


def setup_database():
    """Setup/Reset the database"""
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)

    with app.app_context():
        # Drop all existing tables
        db.drop_all()

        # Create all tables
        db.create_all()

        # Create a default user
        default_user = User(
            username='default_user',
            email='default@example.com'
        )
        db.session.add(default_user)
        db.session.commit()

        print("Database has been reset and initialized with default user")


if __name__ == "__main__":
    setup_database()