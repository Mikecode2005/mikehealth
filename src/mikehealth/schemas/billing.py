"""Billing schemas."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BillingUpdate(BaseModel):
    """Schema for updating billing."""
    balance_due: Decimal = Field(..., ge=0, decimal_places=2, max_digits=10)


class BillingRead(BaseModel):
    """Schema for reading billing information."""
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    name: str
    insurance_id: Optional[str] = None
    balance_due: Decimal