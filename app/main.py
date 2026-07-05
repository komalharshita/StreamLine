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
    upload,
)
from app.upload import upload_router
from app.decision_engine.router import router as decision_feed_router
from app.gemini.routes import router as gemini_api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware

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
    """Liveness/readiness endpoint returning operational state indicators."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


# 5. Register versioned API routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(
    upload_router.router, prefix=settings.API_V1_STR, tags=["Upload"]
)
app.include_router(decision_feed_router)
app.include_router(gemini_api_router)
app.include_router(
    dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"]
)
app.include_router(
    decision.router, prefix=f"{settings.API_V1_STR}/decision", tags=["Decision Engine"]
)
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Gemini Chat"])
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
