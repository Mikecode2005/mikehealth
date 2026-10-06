"""Request logging middleware."""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import structlog

logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for structured request/response logging."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        # Start timing
        start_time = time.perf_counter()

        # Log request
        logger.info(
            "request_started",
            method=request.method,
            url=str(request.url),
            correlation_id=correlation_id,
            client_host=request.client.host if request.client else None,
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.exception(
                "request_failed",
                method=request.method,
                url=str(request.url),
                correlation_id=correlation_id,
                process_time_ms=round(process_time * 1000, 2),
                error=str(e),
            )
            raise

        # Calculate process time
        process_time = time.perf_counter() - start_time

        # Log response
        logger.info(
            "request_completed",
            method=request.method,
            url=str(request.url),
            correlation_id=correlation_id,
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2),
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))

        return response