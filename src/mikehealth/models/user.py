"""User model and role definitions."""
import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mikehealth.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    DOCTOR = "doctor"
    NURSE = "nurse"
    PATIENT = "patient"
    BILLING = "billing"


class User(Base):
    """User account model."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, index=True)
    patient_id: Mapped[Optional[str]] = mapped_column(
        String(36), nullable=True, index=True
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    care_team_memberships: Mapped[list["CareTeamMembership"]] = relationship(
        "CareTeamMembership", back_populates="user", lazy="selectin"
    )

    __table_args__ = (
        Index("ix_users_role_patient_id", "role", "patient_id"),
        UniqueConstraint("email", name="uq_users_email"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"