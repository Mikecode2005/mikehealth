"""FastAPI dependency providers."""
from functools import lru_cache
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.database import get_db
from mikehealth.services.auth import AuthService
from mikehealth.services.patient_record import PatientRecordService
from mikehealth.services.audit_log import AuditLogService


@lru_cache
def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """Get AuthService instance."""
    return AuthService(session)


@lru_cache
def get_patient_record_service(
    session: AsyncSession = Depends(get_db),
) -> PatientRecordService:
    """Get PatientRecordService instance."""
    return PatientRecordService(session)


@lru_cache
def get_audit_log_service(session: AsyncSession = Depends(get_db)) -> AuditLogService:
    """Get AuditLogService instance."""
    return AuditLogService(session)