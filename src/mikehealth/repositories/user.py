"""User repository."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.models.user import User, UserRole


class UserRepository:
    """Repository for user operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(select(User).where(User.id == str(user_id)))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_patient_id(self, patient_id: str) -> Optional[User]:
        """Get user by patient ID."""
        result = await self.session.execute(
            select(User).where(User.patient_id == patient_id)
        )
        return result.scalar_one_or_none()

    async def list_by_role(self, role: UserRole, limit: int = 100, offset: int = 0) -> list[User]:
        """List users by role."""
        result = await self.session.execute(
            select(User).where(User.role == role).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, user: User) -> User:
        """Update user."""
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        """Delete user."""
        await self.session.delete(user)