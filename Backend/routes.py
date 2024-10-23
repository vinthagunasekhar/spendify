from flask import Blueprint, render_template, request, jsonify
from models import db, CreditCard, User
from utils import get_optimal_card
from datetime import datetime

bp = Blueprint('main', __name__)


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/add_card', methods=['POST'])
def add_card():
    try:
        data = request.json
        new_card = CreditCard(
            user_id=1,  # Hardcoded for now, implement user authentication later
            card_name=data['card_name'],
            credit_limit=float(data['credit_limit']),
            cycle_start=int(data['cycle_start']),
            cycle_end=int(data['cycle_end'])
        )
        db.session.add(new_card)
        db.session.commit()
        return jsonify({'message': 'Card added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/get_recommendation', methods=['GET'])
def get_recommendation():
    date_str = request.args.get('date')
    if not date_str:
        date = datetime.now()
    else:
        date = datetime.strptime(date_str, '%Y-%m-%d')

    # Hardcoded user_id=1 for now
    cards = CreditCard.query.filter_by(user_id=1).all()
    if not cards:
        return jsonify({'error': 'No cards found'}), 404

    recommendation = get_optimal_card(date, cards)
    return jsonify({
        'recommended_card': recommendation['card'].card_name,
        'credit_limit': recommendation['card'].credit_limit,
        'reason': recommendation['reason']
    })
