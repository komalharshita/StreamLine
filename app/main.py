import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import (
    auth,
    chat,
    dashboard,
    decision,
    notifications,
    reports,
    simulation,
)
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.decision_engine.router import router as decision_feed_router
from app.gemini.routes import router as gemini_api_router
from app.upload import upload_router

# Initialize Structured/Local logging
setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown lifecycles."""
    logger.info(f"Initializing {settings.PROJECT_NAME} backend foundation.")
    # In production, check connections to databases and cloud storage bucket exists
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME} backend application.")


# Instantiate FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Autonomous Decision Intelligence Platform - Backend API Foundation",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 1. Mount custom logging and instrumentation middleware
app.add_middleware(RequestLoggingMiddleware)

# 2. Configure CORS middleware (cross-origin resource sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3. Register global exception handlers for mapping clean JSON messages
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(f"HTTP error on {request.method} {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        f"Unhandled system error on {request.method} {request.url.path}: {str(exc)}",
        exc_info=True,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "An unexpected server error occurred. Please try again later.",
        },
    )


# 4. Define health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def health_check() -> dict[str, Any]:
    """Liveness/readiness endpoint verifying GCP adapters and Gemini integrations."""
    import os
    components = {
        "fastapi": "healthy",
        "cloud_storage": "healthy",
        "bigquery": "healthy",
        "gemini": "healthy",
        "env_variables": "healthy",
    }
    
    # 1. Verify Env variables
    missing_vars = []
    for var in ["GCS_BUCKET_NAME", "BIGQUERY_DATASET", "GEMINI_API_KEY"]:
        if not getattr(settings, var, None) and not os.environ.get(var):
            missing_vars.append(var)
    if missing_vars:
        components["env_variables"] = "warning"
        
    # 2. Verify Cloud Storage
    try:
        from app.storage.gcs_service import gcs_storage_service
        # Simple client check
        if not gcs_storage_service.client:
            components["cloud_storage"] = "warning"
    except Exception as e:
        logger.error(f"Healthcheck: GCS configuration offline: {str(e)}")
        components["cloud_storage"] = "warning"
        
    # 3. Verify BigQuery
    try:
        from app.bigquery.bigquery_service import bq_ingestion_service
        if not bq_ingestion_service.client:
            components["bigquery"] = "warning"
    except Exception as e:
        logger.error(f"Healthcheck: BigQuery client configuration error: {str(e)}")
        components["bigquery"] = "warning"
        
    # 4. Verify Gemini
    try:
        from app.gemini.gemini_service import gemini_service
        if not gemini_service.api_key:
            components["gemini"] = "warning"
    except Exception as e:
        logger.error(f"Healthcheck: Gemini service config error: {str(e)}")
        components["gemini"] = "warning"

    # Overall Status: if any is warning -> Warning, if critical failure -> Error
    status_val = "healthy"
    if "warning" in components.values():
        status_val = "warning"
    if "error" in components.values():
        status_val = "error"

    return {
        "status": status_val,
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "components": components,
    }


# 5. Register versioned API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(upload_router.router, prefix=settings.API_V1_STR, tags=["Upload"])
app.include_router(decision_feed_router)
app.include_router(gemini_api_router)
app.include_router(dashboard.router)
app.include_router(
    decision.router, prefix=f"{settings.API_V1_STR}/decision", tags=["Decision Engine"]
)
app.include_router(
    chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Gemini Chat"]
)
app.include_router(
    simulation.router,
    prefix=f"{settings.API_V1_STR}/simulation",
    tags=["Simulation & Forecast"],
)
app.include_router(
    reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Analytics Reports"]
)
app.include_router(
    notifications.router,
    prefix=f"{settings.API_V1_STR}/notifications",
    tags=["Notifications"],
)
