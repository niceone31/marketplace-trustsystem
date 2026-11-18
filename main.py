"""FastAPI application factory and lifecycle management."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.error_handlers import register_error_handlers
from api.v1.middleware.rate_limit import setup_rate_limiter
from api.v1.middleware.request_id import RequestIDMiddleware
from api.v1.routers import analyze, cases, dashboard, evaluation, health, reviews
from core.config import get_settings
from core.di import init_db, reset_engine
from core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle context manager initializing logging and database schema."""
    settings = get_settings()
    setup_logging(settings)
    logger.info(
        "marketplace_trust_system_starting",
        environment=settings.environment,
        debug=settings.debug,
    )

    # Initialize database tables and connection pool
    await init_db(settings)
    logger.info("database_tables_initialized")

    yield

    logger.info("marketplace_trust_system_shutting_down")
    await reset_engine()


app = FastAPI(
    title="Marketplace Trust & Compliance System",
    description="Review Authenticity & Counterfeit Detection Agent (PS-13)",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Attach rate limiter and 429 handler
setup_rate_limiter(app)

# Request ID correlation middleware (outermost)
app.add_middleware(RequestIDMiddleware)

# Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# RFC 7807 problem+json error handlers
register_error_handlers(app)

# Mount API v1 routers
settings = get_settings()
prefix = settings.api_v1_str

app.include_router(health.router, prefix=prefix)
app.include_router(analyze.router, prefix=prefix)
app.include_router(cases.router, prefix=prefix)
app.include_router(reviews.router, prefix=prefix)
app.include_router(dashboard.router, prefix=prefix)
app.include_router(evaluation.router, prefix=prefix)


def create_app() -> FastAPI:
    """Return the configured FastAPI app instance."""
    return app


__all__ = ["app", "create_app", "lifespan"]
