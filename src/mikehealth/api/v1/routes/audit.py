"""Audit log routes."""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.api.deps import get_audit_log_service, get_current_user
from mikehealth.models.user import User
from mikehealth.schemas.audit_log import AuditLogRead
from mikehealth.schemas.common import PaginationParams, PaginatedResponse
from mikehealth.services.audit_log import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=PaginatedResponse[AuditLogRead])
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    patient_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    service: AuditLogService = Depends(get_audit_log_service),
    current_user: User = Depends(get_current_user),
):
    """List audit logs with filters (doctors, nurses, billing only)."""
    if current_user.role.value not in {"doctor", "nurse", "billing"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view audit logs",
        )

    params = PaginationParams(page=page, page_size=page_size)
    logs, total = await service.get_logs(
        params=params,
        user_id=user_id,
        patient_id=patient_id,
        action=action,
        start_date=start_date,
        end_date=end_date,
    )
    return PaginatedResponse.create(logs, total, params)