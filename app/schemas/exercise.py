from pydantic import BaseModel, ConfigDict
from typing import Optional, Any


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
    session_type: str
    name: str
    muscle_group: Optional[str] = None
    default_sets: Optional[int] = None
    default_reps: Optional[str] = None
    rir: Optional[str] = None
    notes: Optional[str] = None


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
