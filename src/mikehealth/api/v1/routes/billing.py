"""Billing routes."""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.api.deps import get_patient_record_service, get_current_user
from mikehealth.models.user import User, UserRole
from mikehealth.schemas.billing import BillingRead, BillingUpdate
from mikehealth.schemas.patient_record import PatientRecordBillingView

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/{patient_id}", response_model=BillingRead)
async def get_billing(
    patient_id: str,
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """Get billing information for a patient."""
    billing = await service.get_billing(patient_id, current_user)
    if not billing:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view billing or record not found",
        )
    return BillingRead(
        patient_id=billing.patient_id,
        name=billing.name,
        insurance_id=billing.insurance_id,
        balance_due=billing.balance_due,
    )


@router.patch("/{patient_id}", response_model=BillingRead)
async def update_billing(
    patient_id: str,
    billing_update: BillingUpdate,
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """Update billing information (billing role only)."""
    if current_user.role != UserRole.BILLING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only billing role can update billing",
        )

    billing = await service.update_billing(patient_id, billing_update.balance_due, current_user)
    if not billing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
    return BillingRead(
        patient_id=billing.patient_id,
        name=billing.name,
        insurance_id=billing.insurance_id,
        balance_due=billing.balance_due,
    )