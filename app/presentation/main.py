"""
FastAPI Application Entry Point.

This is the main entry point for the FastAPI application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core import settings
from app.presentation.api.routers.v1.router import router as v1_router
from app.application.services.event_bus import get_event_bus
from app.infrastructure.messaging.handlers import CompanyCreatedHandler, CompanyUpdatedHandler
from app.domain.events.company_created import CompanyCreated
from app.domain.events.company_updated import CompanyUpdated

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup: Register event handlers
    logger.info("Registering event handlers...")
    event_bus = get_event_bus()

    # Register company event handlers
    event_bus.register_handler(CompanyCreated.EVENT_NAME, CompanyCreatedHandler())
    event_bus.register_handler(CompanyUpdated.EVENT_NAME, CompanyUpdatedHandler())

    logger.info("Event handlers registered successfully")

    yield

    # Shutdown: Cleanup resources
    logger.info("Shutting down application...")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    logger.info(f"Creating FastAPI application for environment: {settings.environment}")

    app = FastAPI(
        title=settings.app_name,
        description="Clean Architecture + DDD + SOLID with FastAPI, PostgreSQL, and Redis",
        version=settings.app_version,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins_list(),
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=[settings.cors_allow_methods] if settings.cors_allow_methods == "*" else settings.cors_allow_methods.split(","),
        allow_headers=[settings.cors_allow_headers] if settings.cors_allow_headers == "*" else settings.cors_allow_headers.split(","),
    )

    # Register routers
    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to Test Clean Architecture API",
            "version": settings.app_version,
            "environment": settings.environment,
            "docs": "/docs" if settings.debug else "disabled",
            "redoc": "/redoc" if settings.debug else "disabled",
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "version": settings.app_version,
            "environment": settings.environment,
        }

    logger.info("FastAPI application created successfully")
    return app


# Create the app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.presentation.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
