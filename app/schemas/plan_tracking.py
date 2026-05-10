from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


# === Exercise Log (lo que registra el usuario por serie) ===

class ExerciseLogCreate(BaseModel):
    set_number: int = Field(..., ge=1, le=20)
    weight_kg: Optional[float] = Field(None, ge=0, le=999)
    reps_done: Optional[int] = Field(None, ge=0, le=100)
    rir_actual: Optional[str] = None
    rpe: Optional[float] = Field(None, ge=1, le=10)
    completed: bool = True
    notes: Optional[str] = None


class ExerciseLogUpdate(BaseModel):
    weight_kg: Optional[float] = Field(None, ge=0, le=999)
    reps_done: Optional[int] = Field(None, ge=0, le=100)
    rir_actual: Optional[str] = None
    rpe: Optional[float] = Field(None, ge=1, le=10)
    completed: Optional[bool] = None
    notes: Optional[str] = None


class ExerciseLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_exercise_id: int
    user_id: int
    set_number: int
    weight_kg: Optional[float] = None
    reps_done: Optional[int] = None
    rir_actual: Optional[str] = None
    rpe: Optional[float] = None
    completed: bool
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


# === Plan Exercise (ejercicio planificado) ===

class PlanExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_id: int
    name: str
    muscle_group: Optional[str] = None
    sets: int
    reps: str
    rir: Optional[str] = None
    rest_seconds: Optional[int] = None
    tempo: Optional[str] = None
    notes: Optional[str] = None
    alternatives: Optional[str] = None
    sort_order: int


class PlanExerciseWithLogs(PlanExerciseResponse):
    """Ejercicio con sus logs de series"""
    logs: List[ExerciseLogResponse] = []
    best_weight: Optional[float] = None
    last_weight: Optional[float] = None


# === Plan Day (día de entrenamiento) ===

class PlanDayResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    week_id: int
    day_number: int
    day_name: str
    type: str
    session_name: Optional[str] = None
    duration_minutes: Optional[int] = None
    session_notes: Optional[str] = None
    cardio_type: Optional[str] = None
    cardio_duration_min: Optional[int] = None
    cardio_intensity: Optional[str] = None
    cardio_distance_km: Optional[float] = None
    cardio_notes: Optional[str] = None
    status: str
    completed_at: Optional[datetime] = None


class PlanDayWithExercises(PlanDayResponse):
    """Día con todos sus ejercicios y logs"""
    exercises: List[PlanExerciseWithLogs] = []


# === Plan Week (semana del plan) ===

class PlanWeekResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    plan_id: int
    week_number: int
    phase_name: Optional[str] = None
    is_deload: bool
    focus: Optional[str] = None
    progression_notes: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class PlanWeekWithDays(PlanWeekResponse):
    """Semana con sus días"""
    days: List[PlanDayResponse] = []


class PlanWeekDetail(PlanWeekResponse):
    """Semana con días y ejercicios completos"""
    days: List[PlanDayWithExercises] = []


# === Progression / Stats ===

class ExerciseProgressionPoint(BaseModel):
    week_number: int
    phase_name: Optional[str] = None
    max_weight: Optional[float] = None
    avg_weight: Optional[float] = None
    max_reps: Optional[int] = None
    avg_reps: Optional[float] = None
    total_sets_logged: int = 0
    estimated_1rm: Optional[float] = None


class ExerciseProgression(BaseModel):
    exercise_name: str
    plan_id: int
    points: List[ExerciseProgressionPoint] = []
    best_weight_ever: Optional[float] = None
    best_1rm_ever: Optional[float] = None
    trend: str = "stable"  # up, down, stable


class PlanProgressSummary(BaseModel):
    plan_id: int
    total_weeks: int
    weeks_completed: int
    total_days: int
    days_completed: int
    total_exercises: int
    total_sets_logged: int
    unique_exercises: int
    completion_percent: float


# === Day complete request ===

class CompleteDayRequest(BaseModel):
    notes: Optional[str] = None


class CompleteWeekRequest(BaseModel):
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    soreness_level: Optional[int] = Field(None, ge=1, le=10)
    motivation_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None
