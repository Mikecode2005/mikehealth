"""Health check routes."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mikehealth.database import db
from mikehealth.config import get_settings
from mikehealth.schemas.common import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(session: AsyncSession = Depends(db.session)):
    """Health check endpoint."""
    settings = get_settings()

    # Check database connectivity
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    return HealthCheckResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version="0.1.0",
        environment=settings.environment,
        database=db_status,
    )


@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(db.session)):
    """Kubernetes readiness probe."""
    try:
        await session.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}, 503


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}