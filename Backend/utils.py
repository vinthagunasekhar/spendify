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


def get_usage_period(billing_start, billing_end, days):
    start = int(billing_start)
    end = (datetime(2000, 1, start) + timedelta(days=days - 1)).day

    return f"{start} to {end}"


def sort_cards(cards, today):
    today = int(today)
    return sorted(cards, key=lambda x: (today - int(x.billing_start)) % 31)