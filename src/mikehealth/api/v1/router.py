"""Main API v1 router."""
from fastapi import APIRouter

from mikehealth.api.v1.routes import (
    auth_router,
    patients_router,
    billing_router,
    audit_router,
    health_router,
)
from mikehealth.config import get_settings

settings = get_settings()

api_router = APIRouter(prefix=settings.api_prefix)

api_router.include_router(auth_router)
api_router.include_router(patients_router)
api_router.include_router(billing_router)
api_router.include_router(audit_router)
api_router.include_router(health_router)