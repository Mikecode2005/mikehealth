"""Patient record model."""
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Date,
    DateTime,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from mikehealth.database import Base


class PatientRecord(Base):
    """Patient medical record model."""

    __tablename__ = "patient_records"

    patient_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    diagnoses: Mapped[list[str]] = mapped_column(
        String(2000), nullable=False, default="[]"
    )
    clinical_notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    insurance_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    balance_due: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00")
    )
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

    __table_args__ = (
        Index("ix_patient_records_name", "name"),
        Index("ix_patient_records_insurance_id", "insurance_id"),
        UniqueConstraint("patient_id", name="uq_patient_records_patient_id"),
    )

    def __repr__(self) -> str:
        return f"<PatientRecord(patient_id={self.patient_id}, name={self.name})>"