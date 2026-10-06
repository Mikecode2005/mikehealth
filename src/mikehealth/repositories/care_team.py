"""Care team repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.models.care_team import CareTeamMembership
from mikehealth.models.user import User, UserRole


class CareTeamRepository:
    """Repository for care team operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, membership: CareTeamMembership) -> CareTeamMembership:
        """Create a new care team membership."""
        self.session.add(membership)
        await self.session.flush()
        await self.session.refresh(membership)
        return membership

    async def get_by_user_and_patient(
        self, user_id: str, patient_id: str
    ) -> Optional[CareTeamMembership]:
        """Get membership by user and patient."""
        result = await self.session.execute(
            select(CareTeamMembership).where(
                and_(
                    CareTeamMembership.user_id == user_id,
                    CareTeamMembership.patient_id == patient_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_by_patient(self, patient_id: str) -> list[CareTeamMembership]:
        """List all care team members for a patient."""
        result = await self.session.execute(
            select(CareTeamMembership).where(CareTeamMembership.patient_id == patient_id)
        )
        return list(result.scalars().all())

    async def list_by_user(self, user_id: str) -> list[CareTeamMembership]:
        """List all patients a user has access to."""
        result = await self.session.execute(
            select(CareTeamMembership).where(CareTeamMembership.user_id == user_id)
        )
        return list(result.scalars().all())

    async def delete(self, membership: CareTeamMembership) -> None:
        """Delete care team membership."""
        await self.session.delete(membership)

    async def is_user_on_care_team(self, user_id: str, patient_id: str) -> bool:
        """Check if user is on patient's care team."""
        membership = await self.get_by_user_and_patient(user_id, patient_id)
        return membership is not None