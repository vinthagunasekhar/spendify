from datetime import datetime
from typing import Dict, List, Tuple
from decimal import Decimal
from models import CreditCard
from config import Config


def validate_and_format_credit_limit(value: str) -> Tuple[bool, str, str]:
    """Validates and formats credit limit."""
    clean_value = value.replace('$', '').replace(',', '')

    if not clean_value.isdigit():
        return False, '', "Credit limit must contain only numbers"

    amount = Decimal(clean_value)
    if amount < Config.MIN_CREDIT_LIMIT:
        return False, '', f"Credit limit must be at least ${Config.MIN_CREDIT_LIMIT}"

    return True, "${:,.0f}".format(amount), ""


def validate_cycle_date(date_value: str) -> Tuple[bool, str]:
    """Validates a cycle date value."""
    if not str(date_value).isdigit():
        return False, "Cycle date must be a valid number"

    date_int = int(date_value)
    if not 1 <= date_int <= 31:
        return False, "Cycle date must be between 1 and 31"

    return True, ""


def handle_billing_cycle_dates(date_value: int) -> Tuple[int, int]:
    """Determines the start and end dates for billing cycle."""
    if 1 <= date_value <= 31:
        if date_value == 1:
            return 1, 31
        return date_value - 1, date_value - 2 if date_value > 2 else 31
    return None, None


def validate_card_data(data: dict) -> tuple[bool, list[str], dict]:
    """
    Validates and processes the card data provided by the user.
    Returns (is_valid, list of error messages, processed_data)
    """
    errors = []
    processed_data = {}

    # Validate card type
    if 'card_type' not in data:
        errors.append("Card type is required")
    elif data['card_type'] not in Config.AVAILABLE_CARDS:
        errors.append(f"Invalid card type. Must be one of: {', '.join(sorted(Config.AVAILABLE_CARDS))}")
    else:
        processed_data['card_type'] = data['card_type']

    # Validate credit limit
    if 'credit_limit' not in data:
        errors.append("Credit limit is required")
    else:
        try:
            credit_limit = float(str(data['credit_limit']).replace('$', '').replace(',', ''))
            if credit_limit < Config.MIN_CREDIT_LIMIT:
                errors.append(f"Credit limit must be at least ${Config.MIN_CREDIT_LIMIT}")
            else:
                processed_data['credit_limit'] = credit_limit
        except ValueError:
            errors.append("Credit limit must be a valid number")

    # Handle billing cycle dates
    cycle_date = data.get('cycle_date')
    if cycle_date is None:
        errors.append("Cycle date is required")
    else:
        try:
            cycle_date = int(cycle_date)
            if not 1 <= cycle_date <= 31:
                errors.append("Cycle date must be between 1 and 31")
            else:
                if cycle_date == 1:
                    processed_data['cycle_start'] = 1
                    processed_data['cycle_end'] = 31
                else:
                    processed_data['cycle_start'] = cycle_date - 1
                    processed_data['cycle_end'] = cycle_date - 2 if cycle_date > 2 else 31
        except ValueError:
            errors.append("Cycle date must be a valid number between 1 and 31")

    return (len(errors) == 0, errors, processed_data)

def get_optimal_card(date: datetime, cards: List[CreditCard]) -> Dict:
    """Determines optimal card based on billing cycle."""
    day_of_month = date.day

    for card in cards:
        if card.cycle_start <= card.cycle_end:
            if card.cycle_start <= day_of_month <= card.cycle_end:
                return {
                    'card': card,
                    'reason': f'Best timing: falls within {card.card_name} cycle'
                }
        elif day_of_month >= card.cycle_start or day_of_month <= card.cycle_end:
            return {
                'card': card,
                'reason': f'Best timing: falls within {card.card_name} cycle'
            }

    highest_limit_card = max(cards, key=lambda x: x.credit_limit)
    return {
        'card': highest_limit_card,
        'reason': 'Fallback: highest credit limit available'
    }