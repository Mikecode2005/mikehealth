"""Global error handling middleware."""
import traceback
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import structlog
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from mikehealth.schemas.common import ErrorResponse

logger = structlog.get_logger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling and standardized error responses."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
            return await self._handle_exception(request, exc, correlation_id)

    async def _handle_exception(
        self, request: Request, exc: Exception, correlation_id: str
    ) -> JSONResponse:
        """Handle different exception types and return standardized responses."""

        # HTTPException - re-raise to let FastAPI handle it
        from fastapi import HTTPException
        if isinstance(exc, HTTPException):
            error = ErrorResponse(
                type="about:blank",
                title=exc.detail if isinstance(exc.detail, str) else "HTTP Error",
                status=exc.status_code,
                detail=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
                instance=str(request.url),
            )
            return JSONResponse(
                status_code=exc.status_code,
                content=error.model_dump(),
                headers={"X-Correlation-ID": correlation_id},
            )

        # Validation errors
        if isinstance(exc, ValueError):
            logger.warning(
                "validation_error",
                correlation_id=correlation_id,
                path=str(request.url),
                error=str(exc),
            )
            error = ErrorResponse(
                type="about:blank",
                title="Validation Error",
                status=422,
                detail=str(exc),
                instance=str(request.url),
            )
            return JSONResponse(
                status_code=422,
                content=error.model_dump(),
                headers={"X-Correlation-ID": correlation_id},
            )

        # Database integrity errors
        if isinstance(exc, IntegrityError):
            logger.warning(
                "integrity_error",
                correlation_id=correlation_id,
                path=str(request.url),
                error=str(exc.orig),
            )
            error = ErrorResponse(
                type="about:blank",
                title="Conflict",
                status=409,
                detail="Resource already exists or violates constraints",
                instance=str(request.url),
            )
            return JSONResponse(
                status_code=409,
                content=error.model_dump(),
                headers={"X-Correlation-ID": correlation_id},
            )

        # Database errors
        if isinstance(exc, SQLAlchemyError):
            logger.error(
                "database_error",
                correlation_id=correlation_id,
                path=str(request.url),
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            error = ErrorResponse(
                type="about:blank",
                title="Internal Server Error",
                status=500,
                detail="A database error occurred",
                instance=str(request.url),
            )
            return JSONResponse(
                status_code=500,
                content=error.model_dump(),
                headers={"X-Correlation-ID": correlation_id},
            )

        # Unhandled exceptions
        logger.exception(
            "unhandled_exception",
            correlation_id=correlation_id,
            path=str(request.url),
            error=str(exc),
            traceback=traceback.format_exc(),
        )
        error = ErrorResponse(
            type="about:blank",
            title="Internal Server Error",
            status=500,
            detail="An unexpected error occurred",
            instance=str(request.url),
        )
        return JSONResponse(
            status_code=500,
            content=error.model_dump(),
            headers={"X-Correlation-ID": correlation_id},
        )