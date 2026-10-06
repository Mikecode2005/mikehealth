"""Audit log service."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.models.audit_log import AuditLog
from mikehealth.models.user import User
from mikehealth.repositories.audit_log import AuditLogRepository
from mikehealth.schemas.common import PaginationParams


class AuditLogService:
    """Audit log business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.audit_repo = AuditLogRepository(session)

    async def log_action(
        self,
        user: User,
        action: str,
        patient_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log an action to the audit log."""
        log = AuditLog(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            user_id=user.id,
            role=user.role.value,
            action=action,
            patient_id=patient_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.audit_repo.create(log)

    async def get_logs(
        self,
        params: PaginationParams,
        user_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[AuditLog], int]:
        """Get audit logs with filters."""
        return await self.audit_repo.list_all(
            params=params,
            user_id=user_id,
            patient_id=patient_id,
            action=action,
            start_date=start_date,
            end_date=end_date,
        )