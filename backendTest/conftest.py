import pytest
import tempfile
import os
import sys
from datetime import datetime
import uuid

# Add the Backend directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_path = os.path.join(project_root, 'Backend')
sys.path.insert(0, backend_path)

from main import create_app
from models import db, User, CreditCard


@pytest.fixture(scope='function')
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()

    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })

    # Create the database and load test data
    with app.app_context():
        # Drop all existing tables
        db.drop_all()
        # Create all tables fresh
        db.create_all()

        # Verify tables are created
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print("Created tables:", tables)
        for table in tables:
            print(f"Columns in {table}:", [col['name'] for col in inspector.get_columns(table)])

    yield app

    # Cleanup after test
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def test_user(app):
    """Create a test user with unique username and email."""
    with app.app_context():
        # Generate unique values for each test
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user


@pytest.fixture(scope='function')
def test_cards(app, test_user):
    """Create test credit cards."""
    with app.app_context():
        cards = [
            CreditCard(
                user_id=test_user.id,
                card_name='CIBC',
                credit_limit=5000,
                billing_start_date=1,
                billing_end_date=15,
                created_at=datetime.utcnow()
            ),
            CreditCard(
                user_id=test_user.id,
                card_name='RBC',
                credit_limit=10000,
                billing_start_date=15,
                billing_end_date=30,
                created_at=datetime.utcnow()
            )
        ]

        for card in cards:
            db.session.add(card)
        db.session.commit()

        return cards


@pytest.fixture
def auth_headers():
    """Return headers that are required for authenticated requests."""
    return {'Content-Type': 'application/json'}