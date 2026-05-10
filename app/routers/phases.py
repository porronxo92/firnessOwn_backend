from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.phase import Phase
from app.models.exercise import Exercise
from app.schemas.phase import PhaseResponse
from app.schemas.exercise import ExerciseResponse

router = APIRouter()


@router.get("", response_model=List[PhaseResponse])
async def get_phases(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Phase).order_by(Phase.num))
    return result.scalars().all()


@router.get("/{phase_id}", response_model=PhaseResponse)
async def get_phase(phase_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Phase).where(Phase.id == phase_id))
    phase = result.scalar_one_or_none()
    if not phase:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Phase not found")
    return phase


@router.get("/{phase_id}/exercises", response_model=List[ExerciseResponse])
async def get_phase_exercises(
    phase_id: int,
    session_type: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Exercise).where(Exercise.phase_id == phase_id)
    if session_type:
        query = query.where(Exercise.session_type == session_type)
    query = query.order_by(Exercise.sort_order)
    result = await db.execute(query)
    return result.scalars().all()
