from datetime import datetime, timedelta
import calendar


def get_days_in_month(year, month):
    return calendar.monthrange(year, month)[1]


def calculate_billing_days(start_date, end_date):
    start = int(start_date)
    end = int(end_date)

    if end < start:
        # Billing period crosses month boundary
        days_in_month = get_days_in_month(datetime.now().year, datetime.now().month)
        return (days_in_month - start) + end + 1
    else:
        return (end - start) + 1


def get_next_date(date):
    date = int(date)
    return 1 if date == 31 else date + 1


def assign_usage_periods(cards):
    # Sort cards by limit (highest to lowest, None last)
    sorted_cards = sorted(cards, key=lambda x: (x.limit is None, -1 if x.limit is None else -x.limit))

    # Assign usage periods based on billing cycles and limits
    for i, card in enumerate(sorted_cards):
        if i == 0:  # Highest limit card
            card.set_usage_period(get_next_date(card.billing_end), sorted_cards[1].billing_end)
        elif i == len(sorted_cards) - 1:  # Last card
            card.set_usage_period(get_next_date(sorted_cards[i - 1].billing_end), card.billing_end)
        else:  # Middle cards
            card.set_usage_period(get_next_date(sorted_cards[i - 1].billing_end), sorted_cards[i + 1].billing_end)

    return sorted_cards


def sort_cards(cards, today):
    today = int(today)
    return sorted(cards, key=lambda x: (today - x.usage_start) % 31)