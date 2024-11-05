class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///credit_cards.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Predefined list of available credit cards
    AVAILABLE_CARDS = {
        'CIBC',
        'TD',
        'RBC',
        'American Express',
        'BMO',
        'Scotia Bank',
        'Capital One',
        'PC Financial'
    }

    # Minimum credit limit allowed
    MIN_CREDIT_LIMIT = 500