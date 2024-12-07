from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.credit_card import CreditCard
from app.models.user import User
from app.schemas.creditcard import CreditCardCreate, CreditCardCreateResponse, CreditCardEdit, CreditCardResponse, CreditCardEditResponse
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

@router.put(
    "/edit-credit-card/{card_id}",
    response_model=CreditCardEditResponse,
    responses={
        400: {"model": ErrorResponseSchema},
        401: {"model": ErrorResponseSchema},
        403: {"model": ErrorResponseSchema},
        404: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema}
    },
    summary="Edit Credit Card Details",
    description="""
    Edit an existing credit card's details. Users can only edit:
    - Credit limit (minimum 500)
    - Billing cycle dates (must be consecutive days)

    Note: Card name cannot be changed. At least one field must be provided for update.
    """
)
async def edit_credit_card(
        card_id: int,
        card_data: CreditCardEdit,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> CreditCardEditResponse:
    """
    Edit credit card details for the authenticated user.

    Args:
        card_id: ID of the credit card to edit
        card_data: New credit card details
        current_user: Currently authenticated user (from JWT token)
        db: Database session

    Returns:
        CreditCardEditResponse: Updated credit card details

    Raises:
        HTTPException: For various error conditions
    """
    try:
        # First, check if any fields were provided for update
        if not any([
            card_data.credit_limit,
            card_data.billing_start_date,
            card_data.billing_end_date
        ]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "status": "error",
                    "message": "No fields provided for update. Please provide at least one field to update.",
                    "details": None
                }
            )

        # Fetch the existing card and verify it exists
        card = db.query(CreditCard).filter(
            CreditCard.id == card_id,
            CreditCard.status == True  # Only active cards can be edited
        ).first()

        # Handle card not found
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": "Credit card not found in our records.",
                    "details": None
                }
            )

        # Verify card belongs to current user
        if card.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "status": "error",
                    "message": "You don't have permission to edit this credit card",
                    "details": None
                }
            )

        # Update provided fields
        if card_data.credit_limit:
            card.credit_limit = card_data.credit_limit

        if card_data.billing_start_date and card_data.billing_end_date:
            card.billing_start_date = card_data.billing_start_date
            card.billing_end_date = card_data.billing_end_date

        # Commit changes to database
        db.commit()
        db.refresh(card)

        # Create dynamic success message based on what was updated
        success_message = "Credit card updated successfully! 💳"
        updates = []
        if card_data.credit_limit:
            updates.append(f"credit limit to ${card_data.credit_limit:,}")
        if card_data.billing_start_date:
            updates.append(f"billing cycle to {card_data.billing_start_date}-{card_data.billing_end_date}")

        if updates:
            success_message += f" Updated {' and '.join(updates)}."
        card_response = CreditCardResponse.model_validate(card)
        # Return success response
        return CreditCardEditResponse(
            status="success",
            message=success_message,
            data=card_response
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        db.rollback()
        raise

    except Exception as e:
        # Handle unexpected errors
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Failed to update credit card",
                "details": str(e)
            }
        )


@router.put(
    "/delete-credit-card/{card_id}",
    response_model=CreditCardEditResponse,
    responses={
        400: {"model": ErrorResponseSchema},
        401: {"model": ErrorResponseSchema},
        403: {"model": ErrorResponseSchema},
        404: {"model": ErrorResponseSchema}
    },
    summary="Delete Credit Card",
    description="""
    Soft delete a credit card by setting its status to inactive (False).
    This preserves the card's history while removing it from active use.
    The card won't be permanently deleted from the database.
    """
)
async def delete_credit_card(
        card_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
) -> CreditCardEditResponse:
    """
    Soft delete a credit card by setting its status to False.

    This endpoint performs several important checks:
    1. Verifies the card exists and is currently active
    2. Ensures the user owns the card they're trying to delete
    3. Updates the card's status while preserving its data

    Args:
        card_id: ID of the credit card to delete
        current_user: Currently authenticated user (from JWT token)
        db: Database session

    Returns:
        CreditCardEditResponse: Updated credit card details showing inactive status

    Raises:
        HTTPException: For various error conditions (card not found, unauthorized, etc.)
    """
    try:
        # First, fetch the card and verify it exists and is active
        card = db.query(CreditCard).filter(
            CreditCard.id == card_id,
            CreditCard.status == True  # Only active cards can be deleted
        ).first()

        # Handle card not found or already deleted
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "status": "error",
                    "message": "Credit card not found or is already deleted",
                    "details": None
                }
            )

        # Verify card belongs to current user
        if card.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "status": "error",
                    "message": "You don't have permission to delete this credit card",
                    "details": None
                }
            )

        # Perform the soft delete by setting status to False
        card.status = False

        # Commit changes to database
        db.commit()
        db.refresh(card)

        # Create a meaningful success message
        success_message = (
            f"Successfully removed {card.card_name} from your active cards! 💳❌ "
            "You can always add it back later if needed."
        )

        # Convert the SQLAlchemy model to Pydantic response
        card_response = CreditCardResponse.model_validate(card)

        return CreditCardEditResponse(
            status="success",
            message=success_message,
            data=card_response
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "Failed to delete credit card",
                "details": str(e)
            }
        )