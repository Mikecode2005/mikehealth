"""API v1 routes package."""
from mikehealth.api.v1.routes.auth import router as auth_router
from mikehealth.api.v1.routes.patients import router as patients_router
from mikehealth.api.v1.routes.billing import router as billing_router
from mikehealth.api.v1.routes.audit import router as audit_router
from mikehealth.api.v1.routes.health import router as health_router

__all__ = [
    "auth_router",
    "patients_router",
    "billing_router",
    "audit_router",
    "health_router",
]