"""Main application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import structlog

from mikehealth.config import get_settings
from mikehealth.database import db
from mikehealth.api.v1.router import api_router
from mikehealth.middleware.logging import LoggingMiddleware
from mikehealth.middleware.error_handling import ErrorHandlingMiddleware


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()

    # Startup
    logger.info("starting_application", app_name=settings.app_name, environment=settings.environment)
    db.connect()
    logger.info("database_connected")

    # Create tables (in production, use Alembic migrations instead)
    if settings.environment == "development":
        await db.create_all()
        logger.info("database_tables_created")

    yield

    # Shutdown
    logger.info("shutting_down_application")
    await db.disconnect()
    logger.info("database_disconnected")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="mikehealth API",
        description="A modern healthcare API for patient records, clinical notes, and billing management",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Add middleware (order matters - first added is outermost)
    app.add_middleware(ErrorHandlingMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Include API routes
    app.include_router(api_router)

    @app.get("/")
    async def root():
        return {
            "name": "mikehealth API",
            "version": "0.1.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "mikehealth.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )