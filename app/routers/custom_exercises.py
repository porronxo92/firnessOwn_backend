from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.database import get_db
from app.models.custom_exercise import CustomExercise
from app.models.user import User
from app.schemas.exercise import CustomExerciseCreate, CustomExerciseResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[CustomExerciseResponse])
async def get_custom_exercises(
    phase_id: Optional[int] = None,
    session_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(CustomExercise).where(CustomExercise.user_id == current_user.id)
    if phase_id:
        query = query.where(CustomExercise.phase_id == phase_id)
    if session_type:
        query = query.where(CustomExercise.session_type == session_type)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CustomExerciseResponse)
async def create_custom_exercise(
    data: CustomExerciseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    exercise = CustomExercise(
        user_id=current_user.id,
        phase_id=data.phase_id,
        session_type=data.session_type,
        name=data.name,
        muscle_group=data.muscle_group,
        default_sets=data.default_sets,
        default_reps=data.default_reps,
        rir=data.rir,
        notes=data.notes,
    )
    db.add(exercise)
    await db.flush()
    await db.refresh(exercise)
    return exercise


@router.put("/{exercise_id}", response_model=CustomExerciseResponse)
async def update_custom_exercise(
    exercise_id: int,
    data: CustomExerciseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CustomExercise).where(
            CustomExercise.id == exercise_id,
            CustomExercise.user_id == current_user.id
        )
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Custom exercise not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(exercise, field, value)

    await db.flush()
    await db.refresh(exercise)
    return exercise


@router.delete("/{exercise_id}")
async def delete_custom_exercise(
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CustomExercise).where(
            CustomExercise.id == exercise_id,
            CustomExercise.user_id == current_user.id
        )
    )
    exercise = result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Custom exercise not found")

    await db.delete(exercise)
    return {"detail": "Custom exercise deleted"}
