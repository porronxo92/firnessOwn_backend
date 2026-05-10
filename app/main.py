from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import phases, exercises, logs, custom_exercises, stats, auth, onboarding, plan_tracking

app = FastAPI(title="Training Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "https://tudominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
        print("✅ Base de datos conectada y tablas verificadas")
    except Exception as e:
        print(f"⚠️  No se pudo conectar a la base de datos: {e}")
        print("   La API arrancará igualmente. Comprueba DATABASE_URL en .env")
