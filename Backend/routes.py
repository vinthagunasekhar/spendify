from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from models import db, CreditCard
from utils import validate_card_data, validate_and_format_credit_limit, get_optimal_card
from config import Config

bp = Blueprint('main', __name__)


def error_response(message, details=None, status=400):
    """Helper function for error responses"""
    return jsonify({
        'success': False,
        'error': message,
        'details': details or []
    }), status


def success_response(data, message=None, status=200):
    """Helper function for success responses"""
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response), status


@bp.route('/api/available_cards', methods=['GET'])
def get_available_cards():
    """Get list of all available credit cards"""
    return jsonify({
        'success': True,
        'cards': sorted(list(Config.AVAILABLE_CARDS))
    })


@bp.route('/api/billing-dates', methods=['GET'])
def get_billing_dates():
    """Get list of available billing dates (1-31)"""
    return success_response({'dates': list(range(1, 32))})


@bp.route('/api/validate-credit-limit', methods=['POST'])
def validate_credit_limit():
    """Validate and format credit limit input"""
    data = request.get_json()
    if not data:
        return error_response('No data provided')

    value = data.get('credit_limit', '')
    is_valid, formatted_value, error = validate_and_format_credit_limit(str(value))

    return success_response({
        'is_valid': is_valid,
        'formatted_value': formatted_value if is_valid else '',
        'error': error if not is_valid else None
    })


@bp.route('/api/cards', methods=['POST'])
def add_card():
    """Add a new credit card"""
    try:
        data = request.get_json()
        if not data:
            return error_response('No data provided')

        is_valid, errors, processed_data = validate_card_data(data)
        if not is_valid:
            return error_response('Validation failed', errors)

        new_card = CreditCard(
            user_id=1,  # Hardcoded for now
            card_name=processed_data['card_name'],
            credit_limit=processed_data['credit_limit'],
            billing_start_date=processed_data['billing_start_date'],
            billing_end_date=processed_data['billing_end_date']
        )

        db.session.add(new_card)
        db.session.commit()

        card_data = {
            'id': new_card.id,
            'card_name': new_card.card_name,
            'credit_limit': new_card.credit_limit,
            'billing_start_date': new_card.billing_start_date,
            'billing_end_date': new_card.billing_end_date
        }
        return success_response({'card': card_data}, 'Card added successfully', 201)

    except Exception as e:
        print(f"Error in add_card: {str(e)}")  # For debugging
        return error_response('Server error', [str(e)], 500)


@bp.route('/api/cards/<int:card_id>', methods=['PUT'])
def edit_card(card_id):
    """Edit an existing credit card"""
    try:
        # Find the card
        card = CreditCard.query.filter_by(id=card_id, user_id=1).first()
        if not card:
            return error_response('Card not found', status=404)

        # Validate the update data
        data = request.get_json()
        if not data:
            return error_response('No data provided')

        is_valid, errors, processed_data = validate_card_data(data)
        if not is_valid:
            return error_response('Validation failed', errors)

        # Update the card
        card.card_name = processed_data['card_name']
        card.credit_limit = processed_data['credit_limit']
        card.billing_start_date = processed_data['billing_start_date']
        card.billing_end_date = processed_data['billing_end_date']

        db.session.commit()

        card_data = {
            'id': card.id,
            'card_name': card.card_name,
            'credit_limit': card.credit_limit,
            'billing_start_date': card.billing_start_date,
            'billing_end_date': card.billing_end_date
        }
        return success_response({'card': card_data}, 'Card updated successfully')

    except Exception as e:
        print(f"Error in edit_card: {str(e)}")  # For debugging
        return error_response('Server error', [str(e)], 500)


@bp.route('/api/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """Delete a credit card"""
    try:
        # Find the card
        card = CreditCard.query.filter_by(id=card_id, user_id=1).first()
        if not card:
            return error_response('Card not found', status=404)

        # Delete the card
        db.session.delete(card)
        db.session.commit()

        return success_response({}, 'Card deleted successfully')

    except Exception as e:
        print(f"Error in delete_card: {str(e)}")  # For debugging
        return error_response('Server error', [str(e)], 500)


@bp.route('/api/cards', methods=['GET'])
def get_cards():
    """Get all cards for the current user"""
    try:
        cards = CreditCard.query.filter_by(user_id=1).all()
        cards_data = [{
            'id': card.id,
            'card_name': card.card_name,
            'credit_limit': card.credit_limit,
            'billing_start_date': card.billing_start_date,
            'billing_end_date': card.billing_end_date
        } for card in cards]
        return success_response({'cards': cards_data})
    except Exception as e:
        return error_response('Server error', [str(e)], 500)


@bp.route('/', methods=['GET'])
def index():
    """Render the main page"""
    return render_template('index.html')


@bp.route('/api/recommendation', methods=['GET'])
def get_recommendation():
    """Get card recommendation for a specific date"""
    try:
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()

        cards = CreditCard.query.filter_by(user_id=1).all()
        if not cards:
            return error_response('No cards found', status=404)

        recommendation = get_optimal_card(date, cards)
        return success_response({
            'recommended_card': recommendation['card'].card_name,
            'credit_limit': recommendation['card'].credit_limit,
            'reason': recommendation['reason']
        })
    except Exception as e:
        return error_response('Server error', [str(e)], 500)