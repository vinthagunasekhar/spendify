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

    def test_valid_billing_cycles(self):
        """Test valid billing cycles where end date is day before start date"""
        valid_cases = [
            # start_date, end_date, description
            (1, 31, "Month boundary cycle"),
            (15, 14, "Mid-month cycle"),
            (31, 30, "Month end cycle"),
            (20, 19, "Regular cycle"),
            (5, 4, "Early month cycle")
        ]

        for start_date, end_date, description in valid_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == True, \
                f"Failed for {description}: start={start_date}, end={end_date}"
            assert error == "", \
                f"Unexpected error for {description}: {error}"

    def test_invalid_date_ranges(self):
        """Test dates outside valid range (1-31)"""
        invalid_cases = [
            # start_date, end_date, description
            (0, 15, "Start date below range"),
            (32, 15, "Start date above range"),
            (15, 0, "End date below range"),
            (15, 32, "End date above range"),
            (-1, 15, "Negative start date"),
            (15, -1, "Negative end date")
        ]

        for start_date, end_date, description in invalid_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == False, \
                f"Should fail for {description}: start={start_date}, end={end_date}"
            assert error == "Billing dates must be between 1 and 31", \
                f"Wrong error message for {description}"

    def test_non_adjacent_dates(self):
        """Test billing cycles where dates are not adjacent"""
        invalid_cases = [
            # start_date, end_date, expected_error
            (5, 3, "For start date 5, end date must be 4"),
            (15, 13, "For start date 15, end date must be 14"),
            (20, 18, "For start date 20, end date must be 19"),
            (1, 29, "For start date 1, end date must be 31"),
            (3, 31, "For end date 31, start date must be 1")
        ]

        for start_date, end_date, expected_error in invalid_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == False, \
                f"Should fail for non-adjacent dates: start={start_date}, end={end_date}"
            assert error == expected_error, \
                f"Wrong error message. Expected '{expected_error}' but got '{error}'"

    def test_edge_cases(self):
        """Test edge cases and special scenarios"""
        test_cases = [
            # start_date, end_date, is_valid, expected_error
            # Special case: Start date 1
            (1, 31, True, ""),
            (1, 30, False, "For start date 1, end date must be 31"),

            # Special case: End date 31
            (1, 31, True, ""),
            (2, 31, False, "For end date 31, start date must be 1"),

            # Same date cases
            (15, 15, False, "For start date 15, end date must be 14"),
            (1, 1, False, "For start date 1, end date must be 31"),
            (31, 31, False, "For start date 31, end date must be 30")
        ]

        for start_date, end_date, expected_valid, expected_error in test_cases:
            is_valid, error = validate_billing_dates(start_date, end_date)
            assert is_valid == expected_valid, \
                f"Failed for edge case: start={start_date}, end={end_date}"
            assert error == expected_error, \
                f"Wrong error message for edge case: start={start_date}, end={end_date}"




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
        assert is_valid == False
        assert len(errors) == 1
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




# below 2 test cases need to validate.

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