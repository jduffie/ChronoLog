"""
FastAPI application setup for chronograph API.

This module provides the FastAPI application configuration with proper
middleware, error handling, and dependency injection setup.
"""

import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from .api import router
from .api_middleware import (
    ChronographAPIException,
    MetricsMiddleware,
    chronograph_exception_handler,
    general_exception_handler,
    validation_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_chronograph_api_app() -> FastAPI:
    """
    Create and configure the FastAPI application for chronograph API.

    Returns:
        FastAPI: Configured FastAPI application
    """
    app = FastAPI(
        title="ChronoLog Chronograph API",
        description="Comprehensive REST API for chronograph data management",
        version="1.0.0",
        docs_url="/api/v1/chronograph/docs",
        redoc_url="/api/v1/chronograph/redoc",
        openapi_url="/api/v1/chronograph/openapi.json",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)

        # Log metrics
        await MetricsMiddleware.log_request_metrics(
            request, process_time, response.status_code
        )

        return response

    # Add exception handlers
    app.add_exception_handler(ChronographAPIException, chronograph_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Include the chronograph router
    app.include_router(router)

    # Health check endpoint
    @app.get("/api/v1/chronograph/health")
    async def health_check():
        """Health check endpoint for monitoring"""
        return {
            "status": "healthy",
            "service": "chronograph-api",
            "version": "1.0.0",
            "timestamp": time.time()
        }

    # API info endpoint
    @app.get("/api/v1/chronograph/info")
    async def api_info():
        """API information endpoint"""
        return {
            "name": "ChronoLog Chronograph API",
            "version": "1.0.0",
            "description": "REST API for chronograph data management",
            "features": [
                "Session management",
                "Measurement tracking",
                "Source device management",
                "Statistical analysis",
                "Bulk operations",
                "User isolation",
                "Metric-only data storage"
            ],
            "documentation": "/api/v1/chronograph/docs"
        }

    logger.info("Chronograph API application created successfully")
    return app


# Create the application instance
app = create_chronograph_api_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "chronograph.api_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )