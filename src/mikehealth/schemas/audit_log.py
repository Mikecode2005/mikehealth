"""Audit log schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    """Schema for reading audit log entries."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    timestamp: datetime
    user_id: str
    role: str
    action: str
    patient_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None