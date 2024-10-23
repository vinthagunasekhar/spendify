from datetime import datetime, timedelta

class CreditCard:
    def __init__(self, name, billing_start, billing_end, limit):
        self.name = name
        self.billing_start = int(billing_start)
        self.billing_end = int(billing_end)
        self.limit = limit
        self.usage_start = None
        self.usage_end = None
        self.due_date = None

    def set_usage_period(self, start, end):
        self.usage_start = start
        self.usage_end = end

    def set_due_date(self):
        # Assuming due date is 20 days after billing end date
        due_date = datetime(datetime.now().year, datetime.now().month, self.billing_end) + timedelta(days=20)
        self.due_date = due_date.strftime("%b %d")

class CardStorage:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_cards(self):
        return self.cards

card_storage = CardStorage()