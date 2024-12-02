from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.credit_card import CreditCard
from app.models.user import User
from app.schemas.creditcard import CreditCardCreate, CreditCardCreateResponse
from app.api.deps import get_current_user
from app.schemas.base import ErrorResponseSchema
from app.core.constants import CreditCardCompany
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/add-credit-card",
    response_model=CreditCardCreateResponse,
    responses={
        400: {
            "model": ErrorResponseSchema,
            "description": "Invalid credit card details or exact duplicate found"
        },
        401: {
            "model": ErrorResponseSchema,
            "description": "User not authenticated"
        },
        422: {
            "model": ErrorResponseSchema,
            "description": "Validation error in credit card details"
        }
    },
    summary="Add New Credit Card",
    description="""
    Add a new credit card for the authenticated user.

    Users can have multiple cards of the same type as long as at least one detail differs:
    - Different credit limit, or
    - Different billing cycle dates

    Only exact duplicates (same card type, limit, and dates) are rejected.
    """
)
async def add_credit_card(
        card_data: CreditCardCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> CreditCardCreateResponse:
    """
    Add a new credit card with flexible duplicate checking.

    Args:
        card_data: Validated credit card details from request body
        current_user: Currently authenticated user (from token)
        db: Database session

    Returns:
        CreditCardCreateResponse: Newly created credit card details

    Raises:
        HTTPException: If validation fails, exact duplicate found, or database error occurs
    """
    try:
        # Check for exact duplicate (all fields matching)
        existing_exact_card = db.query(CreditCard).filter(
            CreditCard.user_id == current_user.id,
            CreditCard.card_name == card_data.card_name,
            CreditCard.credit_limit == card_data.credit_limit,
            CreditCard.billing_start_date == card_data.billing_start_date,
            CreditCard.billing_end_date == card_data.billing_end_date,
            CreditCard.status == True
        ).first()

        if existing_exact_card:
            # If we found an exact match, provide a detailed error message
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": (
                        f"You already have an identical {card_data.card_name} card with "
                        f"the same credit limit (${card_data.credit_limit:,}) and "
                        f"billing cycle ({card_data.billing_start_date}-{card_data.billing_end_date}). "
                        "To add another card of this type, please use different details."
                    ),
                    "details": {
                        "card_name": card_data.card_name,
                        "credit_limit": card_data.credit_limit,
                        "billing_cycle": f"{card_data.billing_start_date}-{card_data.billing_end_date}"
                    }
                }
            )

        # Get count of same type cards for informative message
        similar_cards_count = db.query(CreditCard).filter(
            CreditCard.user_id == current_user.id,
            CreditCard.card_name == card_data.card_name,
            CreditCard.status == True
        ).count()

        # Create new credit card instance
        new_card = CreditCard(
            user_id=current_user.id,
            card_name=card_data.card_name.value,  # Get string value from enum
            credit_limit=card_data.credit_limit,
            billing_start_date=card_data.billing_start_date,
            billing_end_date=card_data.billing_end_date,
            status=True
        )

        # Add to database
        db.add(new_card)
        db.commit()
        db.refresh(new_card)

        # Create success message with context about existing cards
        success_message = (
            f"Credit card added successfully! 💳 "
            f"This is your {similar_cards_count + 1}{get_number_suffix(similar_cards_count + 1)} "
            f"{card_data.card_name} card."
        )

        # Return success response
        return CreditCardCreateResponse(
            status="success",
            message=success_message,
            data=new_card
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Error adding credit card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Failed to add credit card",
                "details": str(e)
            }
        )


def get_number_suffix(n: int) -> str:
    """
    Returns the appropriate suffix for a number (1st, 2nd, 3rd, 4th, etc.)

    Args:
        n: The number to get a suffix for

    Returns:
        str: The appropriate suffix
    """
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return suffix