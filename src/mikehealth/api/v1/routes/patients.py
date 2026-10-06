"""Patient records routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.api.deps import get_patient_record_service, get_current_user
from mikehealth.models.user import User
from mikehealth.schemas.patient_record import (
    PatientRecordCreate,
    PatientRecordRead,
    PatientRecordUpdate,
    PatientRecordClinicalView,
)
from mikehealth.schemas.clinical_notes import ClinicalNotesUpdate
from mikehealth.schemas.common import PaginationParams, PaginatedResponse

router = APIRouter(prefix="/patients", tags=["Patient Records"])


@router.post("", response_model=PatientRecordRead, status_code=status.HTTP_201_CREATED)
async def create_patient_record(
    record_data: PatientRecordCreate,
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new patient record."""
    return await service.create_record(record_data, current_user)


@router.get("", response_model=PaginatedResponse[PatientRecordRead])
async def list_patient_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """List patient records accessible to the current user."""
    params = PaginationParams(page=page, page_size=page_size)
    records = await service.list_records(current_user, page, page_size)
    return PaginatedResponse.create(records, len(records), params)


@router.get("/{patient_id}", response_model=PatientRecordRead)
async def get_patient_record(
    patient_id: str,
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """Get a patient record by ID."""
    record = await service.get_record(patient_id, current_user)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.patch("/{patient_id}", response_model=PatientRecordRead)
async def update_patient_record(
    patient_id: str,
    record_update: PatientRecordUpdate,
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """Update a patient record."""
    record = await service.update_record(patient_id, record_update, current_user)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this record or record not found",
        )
    return record


@router.patch("/{patient_id}/clinical-notes", response_model=PatientRecordClinicalView)
async def update_clinical_notes(
    patient_id: str,
    notes_update: ClinicalNotesUpdate,
    service=Depends(get_patient_record_service),
    current_user: User = Depends(get_current_user),
):
    """Update clinical notes for a patient."""
    record = await service.update_clinical_notes(patient_id, notes_update.clinical_notes, current_user)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update clinical notes or record not found",
        )
    return record