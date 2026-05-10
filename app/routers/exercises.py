from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseResponse

router = APIRouter()


@router.get("", response_model=List[ExerciseResponse])
async def get_exercises(
    phase_id: Optional[int] = None,
    session_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Exercise)
    if phase_id:
        query = query.where(Exercise.phase_id == phase_id)
    if session_type:
        query = query.where(Exercise.session_type == session_type)
    query = query.order_by(Exercise.sort_order)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise
