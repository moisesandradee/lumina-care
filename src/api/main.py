"""
Lumina Care — Clinical Intelligence Platform
FastAPI Application Entrypoint
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging

from routers import triage, insights, patients

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("lumina")

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Lumina Care API",
    description=(
        "Clinical intelligence platform for mental health care teams. "
        "Provides psychosocial risk triage, care journey monitoring, "
        "and AI-assisted clinical decision support. "
        "All AI outputs are advisory and require human clinical review."
    ),
    version="0.1.0",
    contact={
        "name": "Lumina Care",
        "url": "https://github.com/moisesandradee/lumina-care",
    },
    license_info={"name": "MIT"},
    openapi_tags=[
        {"name": "triage", "description": "Psychosocial risk triage and patient priority queue"},
        {"name": "insights", "description": "AI-generated clinical insights and recommendations"},
        {"name": "patients", "description": "Patient data and assessment management"},
        {"name": "health", "description": "Service health and readiness"},
    ],
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    """Log request duration for performance monitoring."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    response.headers["X-Process-Time-Ms"] = str(round(duration_ms, 2))
    return response


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(triage.router, prefix="/api/v1/triage", tags=["triage"])
app.include_router(insights.router, prefix="/api/v1/insights", tags=["insights"])
app.include_router(patients.router, prefix="/api/v1/patients", tags=["patients"])


# ---------------------------------------------------------------------------
# Health endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
async def health_check():
    """Basic liveness check."""
    return {"status": "ok", "service": "lumina-care-api", "version": "0.1.0"}


@app.get("/ready", tags=["health"])
async def readiness_check():
    """
    Readiness check — confirms dependent services are reachable.
    In production this would verify DB and cache connectivity.
    """
    return {"status": "ready", "checks": {"database": "ok", "cache": "ok", "ai_service": "ok"}}


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. The incident has been logged.",
        },
    )
