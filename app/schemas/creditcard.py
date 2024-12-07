from pydantic import BaseModel, Field, validator, model_validator
from app.schemas.base import BaseSchema, ResponseSchema
from typing import Optional, Dict
from app.core.constants import CreditCardCompany
import re
from datetime import datetime

class CreditCardCreate(BaseModel):
    '''
    Schema for creating a new credit card with strict validations.
    All fields are required , and clear error messages are provided for each field.
    '''
    #Define card_name field with custom error message
    card_name : CreditCardCompany= Field(
        ..., #Required field
        description="Name of the credit card(must be from approved list)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Credit card name must be from our approved list.",
                "required": "Credit card name is required."
        }
        }
    )

    #Define credit_limit field with custom error message
    credit_limit: int= Field(
        ...,
        ge=500, #Minimum value allowed is 500
        description="Credit limit of the credit card(must be minimum 500 and should contains only numbers)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Credit limit must be a whole number.",
                "required": "Credit limit is required.",
                "ge": "Credit limit must be minimum 500."
            }
        }
    )

    # Define billing dates with custom error messages
    billing_end_date: int = Field(
        ...,
        ge=1,
        le=31,
        description="Day of month billing cycle ends (1-31)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Billing end date must be a number",
                "required": "Please provide the billing end date",
                "ge": "Billing end date must be between 1 and 31",
                "le": "Billing end date must be between 1 and 31"
            }
        }
    )
    billing_start_date: int = Field(
        ...,
        ge=1,
        le=31,
        description="Day of month billing cycle starts (1-31)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Billing start date must be a number",
                "required": "Please provide the billing start date",
                "ge": "Billing start date must be between 1 and 31",
                "le": "Billing start date must be between 1 and 31"
            }
        }
    )

    @model_validator(mode='before')
    @classmethod
    def check_all_fields_present(cls, values: Dict) -> Dict:
        """
        Validates that all required fields are present in the request.
        Provides clear error messages for each missing field.
        """
        required_fields = {
            'card_name': 'Credit card name',
            'credit_limit': 'Credit limit',
            'billing_start_date': 'Billing start date',
            'billing_end_date': 'Billing end date'
        }

        missing_fields = []
        for field, display_name in required_fields.items():
            if field not in values or values[field] is None:
                missing_fields.append(display_name)

        if missing_fields:
            raise ValueError(
                f"The following required fields are missing: {', '.join(missing_fields)}. "
                "Please provide all required information."
            )

        return values

    @validator('credit_limit')
    def validate_credit_limit_format(cls, value):
        """
        Ensures credit limit contains only numbers and meets minimum requirement.
        Provides clear error message for invalid formats.
        """
        if not str(value).isdigit():
            raise ValueError(
                "Credit limit must contain only numbers (0-9). "
                "Please remove any special characters or decimal points."
            )
        return value

    @validator('billing_start_date')
    def validate_billing_dates(cls, start_date, values):
        """
        Validates that billing start date is adjacent to end date in the cycle.
        The cycle is considered 1-31, where 1 follows 31.
        Provides clear error messages for invalid date combinations.
        """
        if 'billing_end_date' not in values:
            raise ValueError(
                "Both billing start and end dates are required. "
                "Please provide the billing end date."
            )

        end_date = values['billing_end_date']

        # Handle the special case where end_date is 1
        if end_date == 1:
            if start_date != 31:
                raise ValueError(
                    "For a billing cycle ending on the 1st of the month, "
                    "the start date must be the 31st of the previous month."
                )
            return start_date

        # For all other cases, start date should be end_date - 1
        if start_date != end_date - 1:
            raise ValueError(
                f"Invalid billing cycle dates. For a billing cycle ending on the {end_date}th, "
                f"the start date must be the {end_date - 1}th. Please adjust your dates "
                "to be consecutive."
            )

        return start_date

    model_config = {
        "json_schema_extra": {
            "example": {
                "card_name": "Scotia Bank",
                "credit_limit": 5000,
                "billing_start_date": 4,
                "billing_end_date": 5
            }
        }
    }

class CreditCardResponse(BaseSchema):
    """
    Schema for credit card response data.
    This inherits from BaseSchema to include id and timestamps.
    Used when returning credit card information to the client.
    """
    card_name: str
    credit_limit: int
    billing_start_date: int
    billing_end_date: int
    status: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "card_name": "BMO Credit Card",
                "credit_limit": 5000,
                "billing_start_date": 4,
                "billing_end_date": 5,
                "status": True,
                "user_id": 1,
                "created_at": "2024-12-02T10:00:00",
                "updated_at": "2024-12-02T10:00:00"
            }
        }

class CreditCardCreateResponse(ResponseSchema[CreditCardResponse]):
    """
    Wrapper response schema for credit card creation.
    This follows our standard API response format:
    {
        "status": "success",
        "message": "Credit card added successfully",
        "data": { credit card details }
    }
    """
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Credit card added successfully! 💳",
                "data": {
                    "id": 1,
                    "card_name": "PC Optimum",
                    "credit_limit": 5000,
                    "billing_start_date": 4,
                    "billing_end_date": 5,
                    "status": True,
                    "user_id": 1,
                    "created_at": "2024-12-02T10:00:00",
                    "updated_at": "2024-12-02T10:00:00"
                }
            }
        }

class CreditCardEdit(BaseModel):
    '''
    Schema for editing credit card details.
    Only allows updating credit limit and billing dates.
    This schema enforces our business rule that card names cannot be changed while editing credit card details.
    '''
    credit_limit: Optional[int]= Field(
        None,
        ge=500,
        description="Credit limit of the credit card(must be minimum 500 and should contains only numbers)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Credit limit must be a whole number.",
                "ge": "Credit limit must be minimum 500."
            }
        }
    )
    billing_start_date: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="New billing cycle start date (1-31)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Billing start date must be a number",
                "ge": "Billing start date must be between 1 and 31",
                "le": "Billing start date must be between 1 and 31"
            }
        }
    )

    billing_end_date: Optional[int] = Field(
        None,
        ge=1,
        le=31,
        description="New billing cycle end date (1-31)",
        json_schema_extra={
            "error_messages": {
                "type_error": "Billing end date must be a number",
                "ge": "Billing end date must be between 1 and 31",
                "le": "Billing end date must be between 1 and 31"
            }
        }
    )

    @model_validator(mode='after')
    def validate_billing_dates(self):
        """
        Validates that if either billing date is provided, both must be provided
        and they must be consecutive days in the billing cycle.
        """
        start_date = self.billing_start_date
        end_date = self.billing_end_date

        # If either date is provided, both must be provided
        if (start_date is not None and end_date is None) or \
                (end_date is not None and start_date is None):
            raise ValueError(
                "Both billing start and end dates must be provided together"
            )

        # If both dates are provided, validate they are consecutive
        if start_date is not None and end_date is not None:
            # Handle special case where end_date is 1
            if end_date == 1:
                if start_date != 31:
                    raise ValueError(
                        "For a billing cycle ending on the 1st, "
                        "the start date must be the 31st"
                    )
            # For all other cases, start date should be end_date - 1
            elif start_date != end_date - 1:
                raise ValueError(
                    f"Invalid billing cycle dates. For a billing cycle ending on the {end_date}th, "
                    f"the start date must be the {end_date - 1}th"
                )

        return self
    class Config:
        from_attributes = True

class CreditCardEditResponse(ResponseSchema):
    """
    Response schema for credit card edit operation.
    Follows our standard API response format for consistency.
    """
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Credit card updated successfully! 💳 Updated credit limit to $6,000.",
                "data": {
                    "id": 1,
                    "card_name": "BMO Credit Card",
                    "credit_limit": 6000,
                    "billing_start_date": 14,
                    "billing_end_date": 15,
                    "status": True,
                    "user_id": 1,
                    "created_at": "2024-12-02T10:00:00",
                    "updated_at": "2024-12-02T10:00:00"
                }
            }
        }

