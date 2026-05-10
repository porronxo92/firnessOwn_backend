from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


class WorkoutLogCreate(BaseModel):
    exercise_id: Optional[int] = None
    custom_exercise_id: Optional[int] = None
    log_date: date
    weight_kg: Optional[Decimal] = None
    sets_done: Optional[int] = None
    reps_done: Optional[str] = None
    rir_actual: Optional[str] = None
    rpe: Optional[float] = None
    notes: Optional[str] = None


class WorkoutLogUpdate(BaseModel):
    log_date: Optional[date] = None
    weight_kg: Optional[Decimal] = None
    sets_done: Optional[int] = None
    reps_done: Optional[str] = None
    rir_actual: Optional[str] = None
    rpe: Optional[float] = None
    notes: Optional[str] = None


class WorkoutLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    exercise_id: Optional[int] = None
    custom_exercise_id: Optional[int] = None
    log_date: date
    weight_kg: Optional[Decimal] = None
    sets_done: Optional[int] = None
    reps_done: Optional[str] = None
    rir_actual: Optional[str] = None
    rpe: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    exercise_name: Optional[str] = None
    session_type: Optional[str] = None


class CardioLogCreate(BaseModel):
    log_date: date
    type: str
    duration_min: Optional[int] = None
    distance_km: Optional[Decimal] = None
    zone: Optional[str] = None
    elevation_m: Optional[int] = None
    notes: Optional[str] = None


class CardioLogUpdate(BaseModel):
    log_date: Optional[date] = None
    type: Optional[str] = None
    duration_min: Optional[int] = None
    distance_km: Optional[Decimal] = None
    zone: Optional[str] = None
    elevation_m: Optional[int] = None
    notes: Optional[str] = None


class CardioLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    log_date: date
    type: str
    duration_min: Optional[int] = None
    distance_km: Optional[Decimal] = None
    zone: Optional[str] = None
    elevation_m: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None


class ProgressPoint(BaseModel):
    log_date: date
    weight_kg: float
    sets_done: int
    reps_done: str
    estimated_1rm: Optional[float] = None


class ExerciseProgress(BaseModel):
    exercise_id: int
    exercise_name: str
    points: List[ProgressPoint]
    max_weight: float
    first_weight: float
    delta_kg: float
    trend: str
