import pytest
import sys
import os
from datetime import datetime, UTC

# Add the Backend directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
backend_path = os.path.join(project_root, 'Backend')
sys.path.insert(0, backend_path)

from utils import (
    validate_and_format_credit_limit,
    validate_billing_dates,
    validate_card_data,
    calculate_days_until_due,
    get_optimal_card
)
from models import db, CreditCard
from config import Config


class TestCreditLimitValidation:
    """Test cases for credit limit validation function"""

    def test_valid_credit_limits(self):
        """Test valid credit limit inputs (only plain numbers allowed)"""
        test_cases = [
            # input_value, expected_valid, expected_format, expected_error
            ("1000", True, "$1,000", ""),  # Valid plain number
            ("5000", True, "$5,000", ""),  # Valid plain number
            ("10000", True, "$10,000", ""),  # Valid plain number
            ("500000", True, "$500,000", "")  # Valid larger number
        ]

        for input_value, expected_valid, expected_format, expected_error in test_cases:
            is_valid, formatted, error = validate_and_format_credit_limit(input_value)
            assert is_valid == expected_valid, f"Failed for input: {input_value}"
            assert formatted == expected_format, f"Wrong formatting for input: {input_value}"
            assert error == expected_error, f"Unexpected error for input: {input_value}"

    def test_invalid_credit_limits(self):
        """Test invalid credit limit inputs"""
        test_cases = [
            # Cases where input contains non-numeric characters
            ("$1000", False, "", "Credit limit must contain only numbers"),  # No dollar signs allowed
            ("1,000", False, "", "Credit limit must contain only numbers"),  # No commas allowed
            ("1000.00", False, "", "Credit limit must contain only numbers"),  # No decimals allowed
            ("abc", False, "", "Credit limit must contain only numbers"),  # No letters allowed
            ("100a", False, "", "Credit limit must contain only numbers"),  # No mixed content allowed
            ("", False, "", "Credit limit must contain only numbers"),  # Empty string not allowed
            (" ", False, "", "Credit limit must contain only numbers"),  # Spaces not allowed
            ("-1000", False, "", "Credit limit must contain only numbers"),  # No negative sign allowed

            # Cases where input is numeric but below minimum
            ("100", False, "", f"Credit limit must be at least ${Config.MIN_CREDIT_LIMIT}"),  # Below minimum
            ("400", False, "", f"Credit limit must be at least ${Config.MIN_CREDIT_LIMIT}")  # Below minimum
        ]

        for input_value, expected_valid, expected_format, expected_error in test_cases:
            is_valid, formatted, error = validate_and_format_credit_limit(input_value)
            assert is_valid == expected_valid, f"Failed for input: {input_value}"
            assert formatted == expected_format, f"Wrong formatting for input: {input_value}"
            assert error == expected_error, f"Wrong error message for input: {input_value}"


class TestBillingDatesValidation:
    """Test cases for billing dates validation"""

    def test_single_date_validation(self):
        """Test validation of single date input (both start and end)"""
        test_cases = [
            # date, is_valid, expected_error
            (1, True, ""),  # Valid date
            (15, True, ""),  # Valid date
            (31, True, ""),  # Valid date
            (0, False, "Billing dates must be between 1 and 31"),  # Invalid - below range
            (32, False, "Billing dates must be between 1 and 31"),  # Invalid - above range
            (-1, False, "Billing dates must be between 1 and 31"),  # Invalid - negative
        ]

        for date, expected_valid, expected_error in test_cases:
            # Test as start date
            is_valid, error = validate_billing_dates(date, date - 1 if date > 1 else 31)
            assert is_valid == expected_valid, f"Failed for start date: {date}"
            assert error == expected_error, f"Wrong error for start date: {date}"

            # Test as end date
            is_valid, error = validate_billing_dates(date + 1 if date < 31 else 1, date)
            assert is_valid == expected_valid, f"Failed for end date: {date}"
            assert error == expected_error, f"Wrong error for end date: {date}"

    def test_adjacent_dates_validation(self):
        """Test validation of adjacent billing dates"""
        valid_cases = [
            # start_date, end_date
            (5, 4),  # Normal adjacent dates
            (20, 19),  # Normal adjacent dates
            (1, 31),  # Edge case: month boundaries
            (31, 30),  # Edge case: month end
        ]

        for start_date, end_date in valid_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == True, \
                f"Should be valid for adjacent dates: {start_date}, {end_date}"
            assert error == ""

    def test_non_adjacent_dates_validation(self):
        """Test validation of non-adjacent billing dates"""
        invalid_cases = [
            # start_date, end_date
            (5, 10),  # Non-adjacent dates
            (20, 25),  # Non-adjacent dates
            (15, 17),  # Non-adjacent dates
            (1, 15),  # Non-adjacent dates
        ]

        for start_date, end_date in invalid_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == False, \
                f"Should be invalid for non-adjacent dates: {start_date}, {end_date}"
            assert error == "Billing dates must be between 1 and 31"

    def test_edge_cases(self):
        """Test edge cases in billing cycle"""
        test_cases = [
            # start_date, end_date, is_valid, expected_error
            (1, 31, True, ""),  # Valid month boundary cycle
            (31, 30, True, ""),  # Valid month end cycle
            (15, 14, True, ""),  # Valid mid-month cycle
            (1, 1, False, "Billing dates must be between 1 and 31"),  # Same date
            (31, 31, False, "Billing dates must be between 1 and 31"),  # Same date
        ]

        for start_date, end_date, expected_valid, expected_error in test_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == expected_valid, \
                f"Failed for dates: {start_date}, {end_date}"
            assert error == expected_error, \
                f"Wrong error for dates: {start_date}, {end_date}"

class TestCardDataValidation:
    """Test cases for complete card data validation"""

    def test_valid_card_data(self):
        """Test validation with valid card data"""
        valid_data = {
            "card_name": "CIBC",
            "credit_limit": "5000",
            "billing_start_date": 1,
            "billing_end_date": 15
        }

        is_valid, errors, processed = validate_card_data(valid_data)
        assert is_valid == True
        assert len(errors) == 0
        assert processed["card_name"] == "CIBC"
        assert processed["credit_limit"] == 5000.0
        assert processed["billing_start_date"] == 1
        assert processed["billing_end_date"] == 15

    def test_missing_required_fields(self):
        """Test validation when required fields are missing"""
        test_cases = [
            ({}, ["Card name is required", "Credit limit is required",
                  "Billing start date is required", "Billing end date is required"]),
            ({"card_name": "CIBC"}, ["Credit limit is required",
                                     "Billing start date is required",
                                     "Billing end date is required"]),
            ({"credit_limit": "5000"}, ["Card name is required",
                                        "Billing start date is required",
                                        "Billing end date is required"]),
        ]

        for input_data, expected_errors in test_cases:
            is_valid, errors, _ = validate_card_data(input_data)
            assert is_valid == False
            for expected_error in expected_errors:
                assert expected_error in errors

    def test_invalid_card_data(self):
        """Test validation with invalid card data"""
        invalid_data = {
            "card_name": "Invalid Card",
            "credit_limit": "abc",
            "billing_start_date": 0,
            "billing_end_date": 32
        }

        is_valid, errors, _ = validate_card_data(invalid_data)
        assert is_valid == False
        assert any("Invalid card name" in error for error in errors)
        assert any("Credit limit must be a valid number" in error for error in errors)
        assert any("Billing dates must be between 1 and 31" in error for error in errors)


class TestDaysUntilDueCalculation:
    """Test cases for calculating days until payment is due"""

    def test_normal_billing_cycle(self):
        """Test calculations for billing cycles within same month"""
        test_cases = [
            (5, 1, 15, 20),  # Early in cycle
            (10, 1, 15, 20),  # Middle of cycle
            (14, 1, 15, 20),  # End of cycle
            (2, 1, 28, 20),  # Long cycle
        ]

        for purchase_day, start_date, end_date, min_days in test_cases:
            days = calculate_days_until_due(purchase_day, start_date, end_date)
            assert days >= min_days, f"Should have at least {min_days} days for purchase on day {purchase_day}"
            assert isinstance(days, int), "Should return an integer"

    def test_cross_month_billing_cycle(self):
        """Test calculations for billing cycles that cross month boundary"""
        test_cases = [
            (25, 20, 5, 20),  # Purchase after cycle start
            (3, 25, 10, 20),  # Purchase before cycle end
            (28, 25, 5, 20),  # Purchase between cycle
            (26, 25, 5, 20),  # Near start of cycle
            (4, 25, 5, 20),  # Near end of cycle
        ]

        for purchase_day, start_date, end_date, min_days in test_cases:
            days = calculate_days_until_due(purchase_day, start_date, end_date)
            assert days >= min_days, f"Should have at least {min_days} days for purchase on day {purchase_day}"
            assert isinstance(days, int), "Should return an integer"

    def test_edge_cases(self):
        """Test edge cases for billing cycle calculations"""
        test_cases = [
            (1, 1, 1),  # Same day for all
            (31, 31, 31),  # Last day of month
            (15, 15, 15),  # Mid-month same day
            (1, 1, 31),  # Full month cycle
            (31, 1, 31),  # Full month cycle, last day purchase
        ]

        for purchase_day, start_date, end_date in test_cases:
            days = calculate_days_until_due(purchase_day, start_date, end_date)
            assert days > 0, "Should always return positive number of days"
            assert isinstance(days, int), "Should return an integer"


class TestOptimalCardSelection:
    """Test cases for optimal card selection"""

    def test_optimal_selection_logic(self, app, test_user):
        """Test that the optimal card is selected based on billing cycles"""
        with app.app_context():
            cards = [
                CreditCard(
                    user_id=test_user.id,
                    card_name="TD",
                    credit_limit=1000,
                    billing_start_date=20,
                    billing_end_date=19
                ),
                CreditCard(
                    user_id=test_user.id,
                    card_name="CIBC",
                    credit_limit=1000,
                    billing_start_date=25,
                    billing_end_date=24
                ),
                CreditCard(
                    user_id=test_user.id,
                    card_name="RBC",
                    credit_limit=2000,
                    billing_start_date=28,
                    billing_end_date=27
                )
            ]

            for card in cards:
                db.session.add(card)
            db.session.commit()

            # Test dates and expected optimal cards based on billing cycles
            test_cases = [
                # Period 1: 1-19 should recommend RBC
                (datetime(2024, 1, 1), "RBC"),
                (datetime(2024, 1, 10), "RBC"),
                (datetime(2024, 1, 19), "RBC"),

                # Period 2: 20-24 should recommend TD
                (datetime(2024, 1, 20), "TD"),
                (datetime(2024, 1, 22), "TD"),
                (datetime(2024, 1, 24), "TD"),

                # Period 3: 25-27 should recommend CIBC
                (datetime(2024, 1, 25), "CIBC"),
                (datetime(2024, 1, 26), "CIBC"),
                (datetime(2024, 1, 27), "CIBC"),

                # Period 4: 28-31 should recommend RBC again
                (datetime(2024, 1, 28), "RBC"),
                (datetime(2024, 1, 30), "RBC"),
                (datetime(2024, 1, 31), "RBC"),
            ]

            for test_date, expected_card_name in test_cases:
                result = get_optimal_card(test_date, cards)
                assert result is not None, f"Should return a recommendation for {test_date}"
                assert result['card'].card_name == expected_card_name, \
                    f"Wrong card selected for date {test_date}. Expected {expected_card_name} but got {result['card'].card_name}"
                print(f"\nFor date {test_date.strftime('%Y-%m-%d')}:")
                print(f"Selected card: {result['card'].card_name}")
                print(f"Reason: {result['reason']}")

    def test_get_optimal_card_empty_list(self):
        """Test optimal card selection with empty card list"""
        result = get_optimal_card(datetime.now(UTC), [])
        assert result is None, "Should return None for empty card list"

    def test_get_optimal_card_single_card(self, app, test_user):
        """Test optimal card selection with single card"""
        with app.app_context():
            card = CreditCard(
                user_id=test_user.id,
                card_name="TD",
                credit_limit=1000,
                billing_start_date=20,
                billing_end_date=19
            )

            db.session.add(card)
            db.session.commit()

            # Test with a date in the current cycle
            date = datetime(2024, 1, 21)  # A date after billing_start_date
            result = get_optimal_card(date, [card])
            assert result is not None, "Should return a recommendation"
            assert result['card'] == card, "Should return the only available card"
            assert isinstance(result['reason'], str), "Should provide a reason"