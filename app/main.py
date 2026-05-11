import logging
import os

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from app.limiter import limiter
from app.logging_config import configure_logging
from app.routers import phases, exercises, logs, custom_exercises, stats, auth, onboarding, plan_tracking

configure_logging()
logger = logging.getLogger(__name__)

# ── Docs: sólo en entornos no productivos ─────────────────────────────────────
_env = os.getenv("ENVIRONMENT", "development")
_docs_url = None if _env == "production" else "/docs"
_redoc_url = None if _env == "production" else "/redoc"
_openapi_url = None if _env == "production" else "/openapi.json"

app = FastAPI(
    title="Training Tracker API",
    version="1.0.0",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    openapi_url=_openapi_url,
)

# ── Rate limiter ───────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS — orígenes explícitos, métodos y headers restringidos ─────────────────
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:4200").split(",")
cors_origins = [origin.strip() for origin in cors_origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ── Security headers ───────────────────────────────────────────────────────────
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        if _env == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# ── Global exception handler — nunca exponer detalles internos ─────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(phases.router, prefix="/api/phases", tags=["phases"])
app.include_router(exercises.router, prefix="/api/exercises", tags=["exercises"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(custom_exercises.router, prefix="/api/custom-exercises", tags=["custom"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(onboarding.router, prefix="/api/onboarding", tags=["onboarding"])
app.include_router(plan_tracking.router, prefix="/api/tracking", tags=["tracking"])


@app.get("/")
async def root():
    return {"message": "Training Tracker API v1.0.0"}


@app.on_event("startup")
async def startup():
    from app.database import engine, Base
    from app.models import User, Phase, Exercise, CustomExercise, WorkoutLog, CardioLog, UserProfile, GeneratedPlan, WeeklyProgress
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Añadir columnas de generación asíncrona si no existen (migration sin Alembic)
            await conn.execute(text(
                "ALTER TABLE generated_plans ADD COLUMN IF NOT EXISTS "
                "generation_status VARCHAR(20) NOT NULL DEFAULT 'completed'"
            ))
            await conn.execute(text(
                "ALTER TABLE generated_plans ADD COLUMN IF NOT EXISTS "
                "generation_error TEXT"
            ))
        logger.info("Base de datos conectada y tablas verificadas")
    except Exception as e:
        logger.warning("No se pudo conectar a la base de datos: %s. La API arrancará igualmente.", e)
