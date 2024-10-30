from datetime import datetime
from typing import Dict, List, Tuple
from decimal import Decimal
from models import CreditCard
from config import Config


def validate_and_format_credit_limit(value: str) -> Tuple[bool, str, str]:
    """Validates and formats credit limit.
    Input must contain only numbers (0-9).
    Returns (is_valid, formatted_value, error_message)
    """
    # First check: Input must contain only digits
    if not value.isdigit():
        return False, '', "Credit limit must contain only numbers"

    # Convert to Decimal for amount validation
    amount = Decimal(value)
    if amount < Config.MIN_CREDIT_LIMIT:
        return False, '', f"Credit limit must be at least ${Config.MIN_CREDIT_LIMIT}"

    # Format valid amount with $ and commas (only in output)
    return True, "${:,.0f}".format(amount), ""


def validate_billing_dates(start_date: int = None, end_date: int = None) -> Tuple[bool, int, str]:
    """
    Validates and processes billing cycle dates.
    If start_date is provided, calculates end_date (day before).
    If end_date is provided, calculates start_date (day after).
    If both provided, validates they form a valid cycle.

    Returns:
    - bool: Is valid
    - int: Calculated companion date (end_date if start provided, start_date if end provided)
    - str: Error message if any
    """
    # Validate input ranges
    if start_date and not (1 <= start_date <= 31):
        return False, None, "Start date must be between 1 and 31"
    if end_date and not (1 <= end_date <= 31):
        return False, None, "End date must be between 1 and 31"

    # Case 1: Only start_date provided
    if start_date and not end_date:
        calculated_end_date = start_date - 1 if start_date > 1 else 31
        return True, calculated_end_date, ""

    # Case 2: Only end_date provided
    if end_date and not start_date:
        calculated_start_date = end_date + 1 if end_date < 31 else 1
        return True, calculated_start_date, ""

    # Case 3: Both dates provided
    if start_date and end_date:
        # Check if dates are adjacent
        if start_date == 1 and end_date == 31:
            return True, None, ""
        if start_date > 1 and end_date == start_date - 1:
            return True, None, ""

        return False, None, f"Billing dates must be adjacent. For start date {start_date}, end date should be {start_date - 1}"

    return False, None, "At least one date must be provided"

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


def calculate_days_until_due(purchase_day: int, billing_start: int, billing_end: int) -> int:
    """
    Calculate the number of days until payment is due from the purchase date.
    Assumes ~30 day billing cycle and ~21 day grace period.
    """
    AVERAGE_MONTH_DAYS = 30
    GRACE_PERIOD_DAYS = 21

    if billing_start <= billing_end:
        # Normal billing cycle within same month
        if billing_start <= purchase_day <= billing_end:
            return GRACE_PERIOD_DAYS + (billing_end - purchase_day)
        return GRACE_PERIOD_DAYS + AVERAGE_MONTH_DAYS + (billing_end - purchase_day)
    else:
        # Billing cycle crosses month boundary
        if purchase_day >= billing_start or purchase_day <= billing_end:
            if purchase_day >= billing_start:
                # Purchase in current month
                return GRACE_PERIOD_DAYS + (AVERAGE_MONTH_DAYS - purchase_day + billing_end)
            else:
                # Purchase in next month
                return GRACE_PERIOD_DAYS + (billing_end - purchase_day)
        return GRACE_PERIOD_DAYS + AVERAGE_MONTH_DAYS + (billing_end - purchase_day)


def get_optimal_card(date: datetime, cards: List[CreditCard]) -> Dict:
    """
    Determines optimal card based on maximizing time until payment is due.
    Returns card with the longest time until payment is due.
    If multiple cards have the same days until due, returns the one with highest credit limit.
    """
    if not cards:
        return None

    day_of_month = date.day
    cards_with_days = []

    for card in cards:
        days_until_due = calculate_days_until_due(
            day_of_month,
            card.billing_start_date,
            card.billing_end_date
        )
        cards_with_days.append((card, days_until_due))

    # Sort by days until due (descending) and credit limit (descending)
    sorted_cards = sorted(
        cards_with_days,
        key=lambda x: (x[1], x[0].credit_limit),
        reverse=True
    )

    optimal_card = sorted_cards[0][0]
    days_to_pay = sorted_cards[0][1]

    return {
        'card': optimal_card,
        'reason': (f'Best timing: {days_to_pay} days until payment is due '
                   f'(statement closes on the {optimal_card.billing_end_date}th)')
    }