from flask import Flask
from config import Config
from models import db
from routes import bp


def create_app():
    """Initialize and configure the Flask application."""
    try:
        app = Flask(__name__)
        app.config.from_object(Config)

        # Initialize extensions
        db.init_app(app)

        # Register blueprints
        app.register_blueprint(bp)

        # Create database tables
        with app.app_context():
            db.create_all()

        return app

    except Exception as e:
        print(f"Failed to create app: {str(e)}")
        raise


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)