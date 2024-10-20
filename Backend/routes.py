from flask import jsonify, request
from models import CreditCard, card_storage
from utils import calculate_billing_days, get_usage_period, sort_cards
from config import CARD_NAMES


def register_routes(app):
    @app.route('/available-cards', methods=['GET'])
    def get_available_cards():
        return jsonify(CARD_NAMES)

    @app.route('/billing-dates', methods=['GET'])
    def get_billing_dates():
        return jsonify(list(range(1, 32)))

    @app.route('/add-card', methods=['POST'])
    def add_card():
        data = request.json
        errors = validate_card_input(data)

        if errors:
            return jsonify({"errors": errors}), 400

        new_card = CreditCard(
            name=data['name'],
            billing_start=data['billing_start'],
            billing_end=data['billing_end'],
            limit=None if data['limit_option'] == 'B' else int(data['limit_value'])
        )

        card_storage.add_card(new_card)
        return jsonify({"message": "Card added successfully", "card": new_card.__dict__})

    @app.route('/user-cards', methods=['GET'])
    def get_user_cards():
        formatted_cards = []
        for card in card_storage.get_cards():
            formatted_card = card.__dict__.copy()
            if formatted_card['limit'] is not None:
                formatted_card['limit'] = f"${formatted_card['limit']:,}"
            else:
                formatted_card['limit'] = "No Limit"
            formatted_cards.append(formatted_card)
        return jsonify(formatted_cards)

    @app.route('/strategy', methods=['GET'])
    def get_strategy():
        cards = card_storage.get_cards()
        if not cards:
            return jsonify({"error": "No cards added yet"}), 400

        strategy = calculate_strategy(cards)
        return jsonify({'strategy': strategy})


def validate_card_input(data):
    errors = {}
    
    # Validate billing_start
    if 'billing_start' not in data or not isinstance(data['billing_start'], int) or not (1 <= data['billing_start'] <= 31):
        errors['billing_start'] = 'Please select a valid billing start date (1-31).'
    
    # Validate billing_end
    if 'billing_end' not in data or not isinstance(data['billing_end'], int) or not (1 <= data['billing_end'] <= 31):
        errors['billing_end'] = 'Please select a valid billing end date (1-31).'

    # Validate limit_value
    if data.get('limit_option') == 'A':  # Assuming limit_value is only required for specific limit option
        if 'limit_value' not in data or not isinstance(data['limit_value'], (int, float)) or data['limit_value'] <= 0:
            errors['limit_value'] = 'Please enter a valid limit value greater than 0.'

    return errors



def calculate_strategy(cards):
    # Sort cards: No limit cards first, then by credit limit (highest to lowest)
    sorted_cards = sorted(cards, key=lambda x: (x.limit is not None, -1 if x.limit is None else -x.limit))

    # Assign usage periods
    total_days = 30  # We'll use this as a baseline
    assigned_days = 0
    for card in sorted_cards:
        if card == sorted_cards[-1]:  # Last card
            days = total_days - assigned_days
        else:
            days = min(21, total_days - assigned_days)
        card.usage = get_usage_period(card.billing_start, card.billing_end, days)
        assigned_days += days

    # Sort cards based on today's date
    from datetime import datetime
    today = datetime.now().strftime("%d")
    final_sorted_cards = sort_cards(sorted_cards, today)

    strategy = []
    for card in final_sorted_cards:
        card_info = {
            'name': card.name,
            'usage': card.usage,
            'limit': "No Limit" if card.limit is None else f"${card.limit:,}"
        }
        strategy.append(card_info)

    return strategy