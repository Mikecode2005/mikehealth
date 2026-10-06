"""Patient record repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.models.patient_record import PatientRecord


class PatientRecordRepository:
    """Repository for patient record operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, record: PatientRecord) -> PatientRecord:
        """Create a new patient record."""
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def get_by_id(self, patient_id: str) -> Optional[PatientRecord]:
        """Get patient record by ID."""
        result = await self.session.execute(
            select(PatientRecord).where(PatientRecord.patient_id == patient_id)
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> tuple[list[PatientRecord], int]:
        """List all patient records with total count."""
        # Get total count
        count_result = await self.session.execute(
            select(func.count(PatientRecord.patient_id))
        )
        total = count_result.scalar_one()

        # Get paginated results
        result = await self.session.execute(
            select(PatientRecord).limit(limit).offset(offset)
        )
        records = list(result.scalars().all())

        return records, total

    async def update(self, record: PatientRecord) -> PatientRecord:
        """Update patient record."""
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def delete(self, record: PatientRecord) -> None:
        """Delete patient record."""
        await self.session.delete(record)