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


def validate_billing_date(date_value: str) -> Tuple[bool, str]:
    """Validates a billing date value."""
    if not str(date_value).isdigit():
        return False, "Billing date must be a valid number"

    date_int = int(date_value)
    if not 1 <= date_int <= 31:
        return False, "Billing date must be between 1 and 31"

    return True, ""


def validate_billing_dates(start_date: int, end_date: int) -> Tuple[bool, str]:
    """Validates the billing start and end dates."""
    if not (1 <= start_date <= 31 and 1 <= end_date <= 31):
        return False, "Billing dates must be between 1 and 31"

    return True, ""


def validate_card_data(data: dict) -> tuple[bool, list[str], dict]:
    """
    Validates and processes the card data provided by the user.
    Returns (is_valid, list of error messages, processed_data)
    """
    errors = []
    processed_data = {}

    # Validate card name
    if 'card_name' not in data:
        errors.append("Card name is required")
    elif data['card_name'] not in Config.AVAILABLE_CARDS:
        errors.append(f"Invalid card name. Must be one of: {', '.join(sorted(Config.AVAILABLE_CARDS))}")
    else:
        processed_data['card_name'] = data['card_name']

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

    # Validate billing dates
    billing_start = data.get('billing_start_date')
    billing_end = data.get('billing_end_date')

    if billing_start is None:
        errors.append("Billing start date is required")
    if billing_end is None:
        errors.append("Billing end date is required")

    if billing_start is not None and billing_end is not None:
        try:
            start_date = int(billing_start)
            end_date = int(billing_end)

            is_valid, error_msg = validate_billing_dates(start_date, end_date)
            if not is_valid:
                errors.append(error_msg)
            else:
                processed_data['billing_start_date'] = start_date
                processed_data['billing_end_date'] = end_date
        except ValueError:
            errors.append("Billing dates must be valid numbers between 1 and 31")

    return (len(errors) == 0, errors, processed_data)


def get_optimal_card(date: datetime, cards: List[CreditCard]) -> Dict:
    """Determines optimal card based on billing cycle."""
    day_of_month = date.day

    for card in cards:
        if card.billing_start_date <= card.billing_end_date:
            if card.billing_start_date <= day_of_month <= card.billing_end_date:
                return {
                    'card': card,
                    'reason': f'Best timing: falls within {card.card_name} billing cycle'
                }
        elif day_of_month >= card.billing_start_date or day_of_month <= card.billing_end_date:
            return {
                'card': card,
                'reason': f'Best timing: falls within {card.card_name} billing cycle'
            }

    highest_limit_card = max(cards, key=lambda x: x.credit_limit)
    return {
        'card': highest_limit_card,
        'reason': 'Fallback: highest credit limit available'
    }