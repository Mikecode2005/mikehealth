"""Patient record service."""
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.models.patient_record import PatientRecord
from mikehealth.models.user import User, UserRole
from mikehealth.repositories.patient_record import PatientRecordRepository
from mikehealth.repositories.care_team import CareTeamRepository
from mikehealth.schemas.patient_record import (
    PatientRecordCreate,
    PatientRecordUpdate,
    PatientRecordRead,
    PatientRecordClinicalView,
    PatientRecordBillingView,
    PatientRecordPatientView,
)
from mikehealth.services.audit_log import AuditLogService


class PatientRecordService:
    """Patient record business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.record_repo = PatientRecordRepository(session)
        self.care_team_repo = CareTeamRepository(session)
        self.audit_service = AuditLogService(session)

    def _can_view_record(self, user: User, patient_id: str) -> bool:
        """Check if user can view patient record."""
        if user.role in {UserRole.DOCTOR, UserRole.NURSE}:
            return self.care_team_repo.is_user_on_care_team(user.id, patient_id)
        elif user.role == UserRole.PATIENT:
            return user.patient_id == patient_id
        return False

    def _can_update_clinical_notes(self, user: User, patient_id: str) -> bool:
        """Check if user can update clinical notes."""
        if user.role in {UserRole.DOCTOR, UserRole.NURSE}:
            return self.care_team_repo.is_user_on_care_team(user.id, patient_id)
        return False

    def _can_view_billing(self, user: User, patient_id: str) -> bool:
        """Check if user can view billing."""
        if user.role == UserRole.BILLING:
            return True
        elif user.role == UserRole.PATIENT:
            return user.patient_id == patient_id
        return False

    def _get_record_view(self, record: PatientRecord, user: User) -> PatientRecordRead:
        """Get appropriate view of record based on user role."""
        if user.role == UserRole.BILLING:
            return PatientRecordBillingView.model_validate(record)
        elif user.role == UserRole.PATIENT:
            return PatientRecordPatientView.model_validate(record)
        else:
            return PatientRecordRead.model_validate(record)

    async def create_record(
        self, record_create: PatientRecordCreate, user: User
    ) -> PatientRecordRead:
        """Create a new patient record."""
        record = PatientRecord(
            patient_id=str(uuid4()),
            name=record_create.name,
            date_of_birth=record_create.date_of_birth,
            diagnoses=record_create.diagnoses,
            clinical_notes=record_create.clinical_notes,
            insurance_id=record_create.insurance_id,
            balance_due=record_create.balance_due,
        )
        record = await self.record_repo.create(record)
        await self.audit_service.log_action(
            user=user,
            action="create_record",
            patient_id=record.patient_id,
            details=f"Created record for {record.name}",
        )
        return PatientRecordRead.model_validate(record)

    async def get_record(self, patient_id: str, user: User) -> Optional[PatientRecordRead]:
        """Get patient record with appropriate view."""
        if not self._can_view_record(user, patient_id):
            return None

        record = await self.record_repo.get_by_id(patient_id)
        if not record:
            return None

        await self.audit_service.log_action(
            user=user,
            action="view_record",
            patient_id=patient_id,
        )
        return self._get_record_view(record, user)

    async def list_records(
        self, user: User, page: int = 1, page_size: int = 20
    ) -> list[PatientRecordRead]:
        """List patient records user has access to."""
        if user.role == UserRole.PATIENT and user.patient_id:
            record = await self.record_repo.get_by_id(user.patient_id)
            if record:
                return [self._get_record_view(record, user)]
            return []

        records, _ = await self.record_repo.list_all(
            limit=page_size, offset=(page - 1) * page_size
        )
        return [self._get_record_view(r, user) for r in records]

    async def update_record(
        self, patient_id: str, record_update: PatientRecordUpdate, user: User
    ) -> Optional[PatientRecordRead]:
        """Update patient record."""
        if not self._can_view_record(user, patient_id):
            return None

        record = await self.record_repo.get_by_id(patient_id)
        if not record:
            return None

        update_data = record_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)

        record = await self.record_repo.update(record)
        await self.audit_service.log_action(
            user=user,
            action="update_record",
            patient_id=patient_id,
            details=f"Updated fields: {', '.join(update_data.keys())}",
        )
        return PatientRecordRead.model_validate(record)

    async def update_clinical_notes(
        self, patient_id: str, clinical_notes: str, user: User
    ) -> Optional[PatientRecordClinicalView]:
        """Update clinical notes."""
        if not self._can_update_clinical_notes(user, patient_id):
            return None

        record = await self.record_repo.get_by_id(patient_id)
        if not record:
            return None

        record.clinical_notes = clinical_notes
        record = await self.record_repo.update(record)
        await self.audit_service.log_action(
            user=user,
            action="update_clinical_notes",
            patient_id=patient_id,
        )
        return PatientRecordClinicalView.model_validate(record)

    async def get_billing(self, patient_id: str, user: User) -> Optional[PatientRecordBillingView]:
        """Get billing information."""
        if not self._can_view_billing(user, patient_id):
            return None

        record = await self.record_repo.get_by_id(patient_id)
        if not record:
            return None

        await self.audit_service.log_action(
            user=user,
            action="view_billing",
            patient_id=patient_id,
        )
        return PatientRecordBillingView.model_validate(record)

    async def update_billing(
        self, patient_id: str, balance_due: Decimal, user: User
    ) -> Optional[PatientRecordBillingView]:
        """Update billing (billing role only)."""
        if user.role != UserRole.BILLING:
            return None

        record = await self.record_repo.get_by_id(patient_id)
        if not record:
            return None

        record.balance_due = balance_due
        record = await self.record_repo.update(record)
        await self.audit_service.log_action(
            user=user,
            action="update_billing",
            patient_id=patient_id,
            details=f"Balance due updated to {balance_due}",
        )
        return PatientRecordBillingView.model_validate(record)