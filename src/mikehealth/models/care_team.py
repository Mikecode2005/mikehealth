"""Care team membership model."""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mikehealth.database import Base


class CareTeamMembership(Base):
    """Care team membership linking users to patients."""

    __tablename__ = "care_team_memberships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    patient_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("patient_records.patient_id", ondelete="CASCADE"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    assigned_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="care_team_memberships")

    __table_args__ = (
        Index("ix_care_team_user_patient", "user_id", "patient_id"),
        UniqueConstraint("user_id", "patient_id", name="uq_care_team_user_patient"),
    )

    def __repr__(self) -> str:
        return f"<CareTeamMembership(user_id={self.user_id}, patient_id={self.patient_id})>"