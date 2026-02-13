"""
TrustHire — Main Application (SaaS Edition)
Railway-ready: never crashes on missing env vars
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings, validate_production_config
from utils.logger import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENV}")

    # Warn about missing config — but never raise
    validate_production_config()

    logger.info("Application ready — /health endpoint active")
    yield
    logger.info("Shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.APP_VERSION,
        # Show docs always (hide only in strict prod with HIDE_DOCS=true)
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
    )

    # ── MIDDLEWARE ──────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # ── HEALTH (registered FIRST so it always responds) ────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENV,
            "ai_enabled": bool(settings.ANTHROPIC_API_KEY),
            "billing_enabled": bool(settings.STRIPE_SECRET_KEY),
            "db_enabled": bool(settings.DATABASE_URL),
        }

    # ── ROUTES ──────────────────────────────────────────────────────────────
    try:
        from api.auth import router as auth_router
        app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
        logger.info("Auth routes loaded")
    except Exception as e:
        logger.error(f"Auth routes failed: {e}")

    try:
        from api.billing import router as billing_router
        app.include_router(billing_router, prefix=settings.API_V1_PREFIX)
        logger.info("Billing routes loaded")
    except Exception as e:
        logger.warning(f"Billing routes skipped (Stripe not configured?): {e}")

    try:
        from api.analysis import router as analysis_router
        app.include_router(analysis_router, prefix=settings.API_V1_PREFIX, tags=["Analysis"])
        logger.info("Analysis routes loaded")
    except Exception as e:
        logger.error(f"Analysis routes failed: {e}")

    try:
        from api.feedback import router as feedback_router
        app.include_router(feedback_router, prefix=settings.API_V1_PREFIX, tags=["Feedback"])
    except Exception as e:
        logger.warning(f"Feedback routes skipped: {e}")

    try:
        from api.resume import router as resume_router
        app.include_router(resume_router, prefix=settings.API_V1_PREFIX, tags=["Resume"])
        logger.info("Resume optimization routes loaded")
    except Exception as e:
        logger.warning(f"Resume routes skipped: {e}")

    try:
        from api.routes import router as web_router
        app.include_router(web_router)
    except Exception as e:
        logger.warning(f"Web routes skipped: {e}")

    # Static files (dev only)
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")

    # ── GLOBAL ERROR HANDLER ────────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "message": "Unexpected error"},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.ENV == "dev",
        log_level=settings.LOG_LEVEL.lower(),
    )
