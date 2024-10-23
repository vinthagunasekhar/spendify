from datetime import datetime, timedelta
from typing import List
from models import CreditCard


def get_optimal_card(date: datetime, cards: List[CreditCard]) -> dict:
    """
    Determine which credit card to use on a given date based on billing cycles.
    Returns a dict with card details and reason for selection.
    """
    day_of_month = date.day

    for card in cards:
        # Handle month wraparound
        if card.cycle_start <= card.cycle_end:
            if card.cycle_start <= day_of_month <= card.cycle_end:
                return {
                    'card': card,
                    'reason': f'Best timing: falls within {card.card_name} cycle'
                }
        else:  # Cycle crosses month boundary
            if day_of_month >= card.cycle_start or day_of_month <= card.cycle_end:
                return {
                    'card': card,
                    'reason': f'Best timing: falls within {card.card_name} cycle'
                }

    # Fallback to highest limit card if no optimal cycle found
    highest_limit_card = max(cards, key=lambda x: x.credit_limit)
    return {
        'card': highest_limit_card,
        'reason': 'Fallback: highest credit limit available'
    }
