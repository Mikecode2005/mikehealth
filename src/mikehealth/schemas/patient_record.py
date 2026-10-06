"""Patient record schemas."""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientRecordBase(BaseModel):
    """Base patient record schema."""
    patient_id: str = Field(..., pattern="^[0-9a-f-]{36}$")
    name: str = Field(..., min_length=1, max_length=255)
    date_of_birth: date
    diagnoses: list[str] = Field(default_factory=list)
    clinical_notes: str = ""
    insurance_id: Optional[str] = Field(default=None, max_length=100)
    balance_due: Decimal = Field(default=Decimal("0.00"), ge=0)


class PatientRecordCreate(PatientRecordBase):
    """Schema for creating a patient record."""
    pass


class PatientRecordUpdate(BaseModel):
    """Schema for updating a patient record."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    date_of_birth: Optional[date] = None
    diagnoses: Optional[list[str]] = None
    clinical_notes: Optional[str] = None
    insurance_id: Optional[str] = Field(default=None, max_length=100)
    balance_due: Optional[Decimal] = Field(default=None, ge=0)


class PatientRecordRead(PatientRecordBase):
    """Schema for reading patient record (full)."""
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime
    updated_at: datetime


class PatientRecordClinicalView(BaseModel):
    """Clinical view of patient record (doctors/nurses)."""
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    name: str
    date_of_birth: date
    diagnoses: list[str]
    clinical_notes: str
    created_at: datetime
    updated_at: datetime


class PatientRecordBillingView(BaseModel):
    """Billing view of patient record (billing/patient)."""
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    name: str
    insurance_id: Optional[str] = None
    balance_due: Decimal


class PatientRecordPatientView(BaseModel):
    """Patient view of their own record."""
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    name: str
    date_of_birth: date
    diagnoses: list[str]
    clinical_notes: str