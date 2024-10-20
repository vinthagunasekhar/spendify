class CreditCard:
    def __init__(self, name, billing_start, billing_end, limit):
        self.name = name
        self.billing_start = billing_start
        self.billing_end = billing_end
        self.limit = limit

class CardStorage:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_cards(self):
        return self.cards

card_storage = CardStorage()