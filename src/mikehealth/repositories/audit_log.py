"""Audit log repository."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.models.audit_log import AuditLog
from mikehealth.schemas.common import PaginationParams


class AuditLogRepository:
    """Repository for audit log operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, log: AuditLog) -> AuditLog:
        """Create a new audit log entry."""
        self.session.add(log)
        await self.session.flush()
        await self.session.refresh(log)
        return log

    async def list_all(
        self,
        params: PaginationParams,
        user_id: Optional[str] = None,
        patient_id: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[list[AuditLog], int]:
        """List audit logs with filters and pagination."""
        query = select(AuditLog)

        # Apply filters
        conditions = []
        if user_id:
            conditions.append(AuditLog.user_id == user_id)
        if patient_id:
            conditions.append(AuditLog.patient_id == patient_id)
        if action:
            conditions.append(AuditLog.action == action)
        if start_date:
            conditions.append(AuditLog.timestamp >= start_date)
        if end_date:
            conditions.append(AuditLog.timestamp <= end_date)

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(AuditLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()

        # Apply pagination and ordering
        query = query.order_by(desc(AuditLog.timestamp)).limit(params.page_size).offset(
            (params.page - 1) * params.page_size
        )

        result = await self.session.execute(query)
        logs = list(result.scalars().all())

        return logs, total