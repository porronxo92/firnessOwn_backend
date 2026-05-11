from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Any
from enum import Enum


class SessionTypeEnum(str, Enum):
    pull = "pull"
    push = "push"
    legs = "legs"
    cardio = "cardio"


class MuscleGroupEnum(str, Enum):
    back = "back"
    chest = "chest"
    legs = "legs"
    glutes = "glutes"
    shoulders = "shoulders"
    arms = "arms"
    core = "core"


class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phase_id: Optional[int] = None
    session_type: str
    name: str
    muscle_group: Optional[str] = None
    muscle_desc: Optional[str] = None
    default_sets: Optional[int] = None
    default_reps: Optional[str] = None
    rir: Optional[str] = None
    notes: Optional[str] = None
    sort_order: Optional[int] = 0


class ExerciseWithLastLogResponse(ExerciseResponse):
    last_log: Optional[Any] = None


class CustomExerciseCreate(BaseModel):
    phase_id: Optional[int] = None
    session_type: SessionTypeEnum
    name: str = Field(..., min_length=1, max_length=100)
    muscle_group: Optional[MuscleGroupEnum] = None
    default_sets: Optional[int] = Field(None, ge=1, le=20)
    default_reps: Optional[str] = Field(None, max_length=20)
    rir: Optional[str] = Field(None, max_length=10)
    notes: Optional[str] = Field(None, max_length=500)


class CustomExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    phase_id: Optional[int] = None
    session_type: str
    name: str
    muscle_group: Optional[str] = None
    default_sets: Optional[int] = None
    default_reps: Optional[str] = None
    rir: Optional[str] = None
    notes: Optional[str] = None
