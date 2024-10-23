from flask import jsonify, request
from models import CreditCard, card_storage
from utils import assign_usage_periods, sort_cards
from config import CARD_NAMES
from datetime import datetime


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

    if 'name' not in data or data['name'] not in CARD_NAMES:
        errors['name'] = "Please select a valid credit card from the list."

    if 'billing_start' not in data or data['billing_start'] not in range(1, 32):
        errors['billing_start'] = "Please select a valid billing start date (1-31)."

    if 'billing_end' not in data or data['billing_end'] not in range(1, 32):
        errors['billing_end'] = "Please select a valid billing end date (1-31)."

    if 'limit_option' not in data or data['limit_option'] not in ['A', 'B']:
        errors['limit_option'] = "Please select a valid limit option (A or B)."
    elif data['limit_option'] == 'A':
        if 'limit_value' not in data or not data['limit_value'].isdigit() or int(data['limit_value']) <= 0:
            errors['limit_value'] = "Please enter a valid credit limit (positive integer)."

    return errors


def calculate_strategy(cards):
    # Assign usage periods based on the new flexible strategy
    assigned_cards = assign_usage_periods(cards)

    # Set due dates for all cards
    for card in assigned_cards:
        card.set_due_date()

    # Sort cards based on today's date for the final strategy order
    today = datetime.now().day
    final_sorted_cards = sort_cards(assigned_cards, today)

    strategy = []
    for card in final_sorted_cards:
        card_info = {
            'name': card.name,
            'usage': f"{card.usage_start} to {card.usage_end}",
            'limit': "No Limit" if card.limit is None else f"${card.limit:,}",
            'due_date': card.due_date
        }
        strategy.append(card_info)

    return strategy