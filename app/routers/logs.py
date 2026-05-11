from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.workout_log import WorkoutLog
from app.models.exercise import Exercise
from app.models.custom_exercise import CustomExercise
from app.models.user import User
from app.schemas.workout_log import WorkoutLogCreate, WorkoutLogUpdate, WorkoutLogResponse
from app.auth import get_current_user

router = APIRouter()


@router.get("", response_model=List[WorkoutLogResponse])
async def get_logs(
    exercise_id: Optional[int] = None,
    custom_exercise_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    date_from: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(WorkoutLog).where(WorkoutLog.user_id == current_user.id)
    if exercise_id:
        query = query.where(WorkoutLog.exercise_id == exercise_id)
    if custom_exercise_id:
        query = query.where(WorkoutLog.custom_exercise_id == custom_exercise_id)
    if date_from:
        query = query.where(WorkoutLog.log_date >= date_from)
    query = query.order_by(desc(WorkoutLog.log_date), desc(WorkoutLog.created_at)).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    # Enrich with exercise names
    response = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "user_id": log.user_id,
            "exercise_id": log.exercise_id,
            "custom_exercise_id": log.custom_exercise_id,
            "log_date": log.log_date,
            "weight_kg": log.weight_kg,
            "sets_done": log.sets_done,
            "reps_done": log.reps_done,
            "rir_actual": log.rir_actual,
            "rpe": log.rpe,
            "notes": log.notes,
            "created_at": log.created_at,
            "exercise_name": None,
            "session_type": None,
        }
        if log.exercise_id:
            ex = await db.execute(
                select(Exercise.name, Exercise.session_type).where(Exercise.id == log.exercise_id)
            )
            row = ex.one_or_none()
            if row:
                log_dict["exercise_name"] = row.name
                log_dict["session_type"] = row.session_type
        elif log.custom_exercise_id:
            ex = await db.execute(
                select(CustomExercise.name, CustomExercise.session_type).where(CustomExercise.id == log.custom_exercise_id)
            )
            row = ex.one_or_none()
            if row:
                log_dict["exercise_name"] = row.name
                log_dict["session_type"] = row.session_type
        response.append(WorkoutLogResponse(**log_dict))
    return response


@router.post("", response_model=WorkoutLogResponse)
async def create_log(
    log_data: WorkoutLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not log_data.exercise_id and not log_data.custom_exercise_id:
        raise HTTPException(status_code=400, detail="Must provide exercise_id or custom_exercise_id")

    log = WorkoutLog(
        user_id=current_user.id,
        exercise_id=log_data.exercise_id,
        custom_exercise_id=log_data.custom_exercise_id,
        log_date=log_data.log_date,
        weight_kg=log_data.weight_kg,
        sets_done=log_data.sets_done,
        reps_done=log_data.reps_done,
        rir_actual=log_data.rir_actual,
        rpe=log_data.rpe,
        notes=log_data.notes,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    exercise_name = None
    session_type = None
    if log.exercise_id:
        ex = await db.execute(
            select(Exercise.name, Exercise.session_type).where(Exercise.id == log.exercise_id)
        )
        row = ex.one_or_none()
        if row:
            exercise_name = row.name
            session_type = row.session_type
    elif log.custom_exercise_id:
        ex = await db.execute(
            select(CustomExercise.name, CustomExercise.session_type).where(CustomExercise.id == log.custom_exercise_id)
        )
        row = ex.one_or_none()
        if row:
            exercise_name = row.name
            session_type = row.session_type

    return WorkoutLogResponse(
        id=log.id, user_id=log.user_id, exercise_id=log.exercise_id,
        custom_exercise_id=log.custom_exercise_id, log_date=log.log_date,
        weight_kg=log.weight_kg, sets_done=log.sets_done, reps_done=log.reps_done,
        rir_actual=log.rir_actual, rpe=log.rpe, notes=log.notes,
        created_at=log.created_at, exercise_name=exercise_name, session_type=session_type
    )


@router.put("/{log_id}", response_model=WorkoutLogResponse)
async def update_log(
    log_id: int,
    log_data: WorkoutLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(WorkoutLog).where(WorkoutLog.id == log_id, WorkoutLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    update_data = log_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    await db.flush()
    await db.refresh(log)

    exercise_name = None
    if log.exercise_id:
        ex = await db.execute(select(Exercise.name).where(Exercise.id == log.exercise_id))
        exercise_name = ex.scalar_one_or_none()

    return WorkoutLogResponse(
        id=log.id, user_id=log.user_id, exercise_id=log.exercise_id,
        custom_exercise_id=log.custom_exercise_id, log_date=log.log_date,
        weight_kg=log.weight_kg, sets_done=log.sets_done, reps_done=log.reps_done,
        rir_actual=log.rir_actual, rpe=log.rpe, notes=log.notes,
        created_at=log.created_at, exercise_name=exercise_name
    )


@router.delete("/{log_id}")
async def delete_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(WorkoutLog).where(WorkoutLog.id == log_id, WorkoutLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    await db.delete(log)
    return {"detail": "Log deleted"}


@router.get("/today", response_model=List[WorkoutLogResponse])
async def get_today_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    today = date.today()
    query = select(WorkoutLog).where(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.log_date == today
    ).order_by(WorkoutLog.created_at)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/recent", response_model=List[WorkoutLogResponse])
async def get_recent_logs(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    since = date.today() - timedelta(days=days)
    query = select(WorkoutLog).where(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.log_date >= since
    ).order_by(desc(WorkoutLog.log_date))
    result = await db.execute(query)
    return result.scalars().all()
