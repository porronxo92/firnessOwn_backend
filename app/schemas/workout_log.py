from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class CardioTypeEnum(str, Enum):
    bici = "bici"
    trail = "trail"
    carrera = "carrera"
    otro = "otro"


class ZoneEnum(str, Enum):
    z1 = "Z1"
    z2 = "Z2"
    z3 = "Z3"
    z4 = "Z4"
    z5 = "Z5"


class WorkoutLogCreate(BaseModel):
    exercise_id: Optional[int] = None
    custom_exercise_id: Optional[int] = None
    log_date: date
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=999)
    sets_done: Optional[int] = Field(None, ge=1, le=100)
    reps_done: Optional[str] = Field(None, max_length=50)
    rir_actual: Optional[str] = Field(None, max_length=10)
    rpe: Optional[float] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)


class WorkoutLogUpdate(BaseModel):
    log_date: Optional[date] = None
    weight_kg: Optional[Decimal] = Field(None, ge=0, le=999)
    sets_done: Optional[int] = Field(None, ge=1, le=100)
    reps_done: Optional[str] = Field(None, max_length=50)
    rir_actual: Optional[str] = Field(None, max_length=10)
    rpe: Optional[float] = Field(None, ge=1, le=10)
    notes: Optional[str] = Field(None, max_length=500)


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
    type: CardioTypeEnum
    duration_min: Optional[int] = Field(None, ge=1, le=600)
    distance_km: Optional[Decimal] = Field(None, ge=0, le=500)
    zone: Optional[ZoneEnum] = None
    elevation_m: Optional[int] = Field(None, ge=0, le=9000)
    notes: Optional[str] = Field(None, max_length=500)


class CardioLogUpdate(BaseModel):
    log_date: Optional[date] = None
    type: Optional[CardioTypeEnum] = None
    duration_min: Optional[int] = Field(None, ge=1, le=600)
    distance_km: Optional[Decimal] = Field(None, ge=0, le=500)
    zone: Optional[ZoneEnum] = None
    elevation_m: Optional[int] = Field(None, ge=0, le=9000)
    notes: Optional[str] = Field(None, max_length=500)


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
