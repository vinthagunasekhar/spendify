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


def validate_card_data(data: Dict) -> Tuple[bool, List[str], Dict]:
    """Validates and processes card data."""
    errors = []
    processed_data = {}

    # Validate card type
    if 'card_type' not in data:
        errors.append("Card type is required")
    elif data['card_type'] not in Config.AVAILABLE_CARDS:
        errors.append(f"Invalid card type. Must be one of: {', '.join(Config.AVAILABLE_CARDS)}")
    else:
        processed_data['card_type'] = data['card_type']

    # Validate credit limit
    if 'credit_limit' not in data:
        errors.append("Credit limit is required")
    else:
        is_valid, formatted_value, error = validate_and_format_credit_limit(str(data['credit_limit']))
        if not is_valid:
            errors.append(error)
        else:
            processed_data['credit_limit'] = Decimal(formatted_value.replace('$', '').replace(',', ''))

    # Validate cycle date
    cycle_date = data.get('cycle_date')
    if cycle_date is None:
        errors.append("Cycle date is required")
    else:
        is_valid, error = validate_cycle_date(cycle_date)
        if not is_valid:
            errors.append(error)
        else:
            cycle_date = int(cycle_date)
            start_date, end_date = handle_billing_cycle_dates(cycle_date)
            processed_data['cycle_start'] = start_date
            processed_data['cycle_end'] = end_date

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