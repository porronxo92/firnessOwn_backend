from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict


class PhaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    num: int
    name: str
    weeks_start: int
    weeks_end: int
    focus: Optional[str] = None
    description: Optional[str] = None
    series_per_muscle: Optional[str] = None
    rep_range: Optional[str] = None
    rir_target: Optional[str] = None
    rest_seconds_min: Optional[int] = None
    rest_seconds_max: Optional[int] = None


class PhaseWithExercisesResponse(PhaseResponse):
    exercises: Dict[str, List] = {}
