from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List, Optional
from datetime import date, timedelta

from app.database import get_db
from app.models.workout_log import WorkoutLog, CardioLog
from app.models.exercise import Exercise
from app.models.user import User
from app.schemas.workout_log import ExerciseProgress, ProgressPoint, CardioLogCreate, CardioLogResponse
from app.auth import get_current_user

router = APIRouter()


def estimate_1rm(weight: float, reps: int) -> float:
    if reps <= 0 or weight <= 0:
        return 0
    return round(weight * (1 + reps / 30), 1)


@router.get("/progress/{exercise_id}", response_model=ExerciseProgress)
async def get_exercise_progress(
    exercise_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get exercise name
    ex_result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    exercise = ex_result.scalar_one_or_none()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    # Get logs
    query = select(WorkoutLog).where(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.exercise_id == exercise_id,
        WorkoutLog.weight_kg.isnot(None)
    ).order_by(desc(WorkoutLog.log_date)).limit(limit)

    result = await db.execute(query)
    logs = result.scalars().all()

    if not logs:
        return ExerciseProgress(
            exercise_id=exercise_id,
            exercise_name=exercise.name,
            points=[],
            max_weight=0,
            first_weight=0,
            delta_kg=0,
            trend="stable"
        )

    points = []
    for log in reversed(logs):
        reps_val = int(log.reps_done.split(",")[0].split("-")[0]) if log.reps_done else 0
        points.append(ProgressPoint(
            log_date=log.log_date,
            weight_kg=float(log.weight_kg),
            sets_done=log.sets_done or 0,
            reps_done=log.reps_done or "0",
            estimated_1rm=estimate_1rm(float(log.weight_kg), reps_val)
        ))

    weights = [p.weight_kg for p in points]
    max_weight = max(weights)
    first_weight = weights[0]
    last_weight = weights[-1]
    delta_kg = round(last_weight - first_weight, 1)

    if delta_kg > 2:
        trend = "up"
    elif delta_kg < -2:
        trend = "down"
    else:
        trend = "stable"

    return ExerciseProgress(
        exercise_id=exercise_id,
        exercise_name=exercise.name,
        points=points,
        max_weight=max_weight,
        first_weight=first_weight,
        delta_kg=delta_kg,
        trend=trend
    )


@router.get("/maxes")
async def get_maxes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(
        WorkoutLog.exercise_id,
        func.max(WorkoutLog.weight_kg).label("max_weight")
    ).where(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.weight_kg.isnot(None)
    ).group_by(WorkoutLog.exercise_id)

    result = await db.execute(query)
    rows = result.all()

    maxes = []
    for row in rows:
        if row.exercise_id:
            ex = await db.execute(select(Exercise.name).where(Exercise.id == row.exercise_id))
            name = ex.scalar_one_or_none() or "Unknown"
            maxes.append({
                "exercise_id": row.exercise_id,
                "exercise_name": name,
                "max_weight": float(row.max_weight)
            })
    return maxes


@router.get("/volume")
async def get_weekly_volume(
    week: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if week:
        start_date = date.today() - timedelta(weeks=week)
        end_date = start_date + timedelta(days=7)
    else:
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

    query = select(WorkoutLog).where(
        WorkoutLog.user_id == current_user.id,
        WorkoutLog.log_date >= start_date,
        WorkoutLog.log_date < end_date
    )
    result = await db.execute(query)
    logs = result.scalars().all()

    total_sets = sum(log.sets_done or 0 for log in logs)
    total_volume = sum(
        float(log.weight_kg or 0) * (log.sets_done or 0) * int((log.reps_done or "0").split(",")[0].split("-")[0] or 0)
        for log in logs
    )

    return {
        "week_start": start_date.isoformat(),
        "week_end": end_date.isoformat(),
        "total_sets": total_sets,
        "total_volume_kg": round(total_volume, 1),
        "session_count": len(set(log.log_date for log in logs))
    }


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Total sessions
    sessions_result = await db.execute(
        select(func.count(func.distinct(WorkoutLog.log_date))).where(
            WorkoutLog.user_id == current_user.id
        )
    )
    total_sessions = sessions_result.scalar() or 0

    # Total logs
    logs_result = await db.execute(
        select(func.count(WorkoutLog.id)).where(WorkoutLog.user_id == current_user.id)
    )
    total_logs = logs_result.scalar() or 0

    # Last session date
    last_result = await db.execute(
        select(func.max(WorkoutLog.log_date)).where(WorkoutLog.user_id == current_user.id)
    )
    last_session = last_result.scalar()

    return {
        "total_sessions": total_sessions,
        "total_logs": total_logs,
        "last_session": last_session.isoformat() if last_session else None
    }


# Cardio endpoints
@router.get("/cardio", response_model=List[CardioLogResponse])
async def get_cardio_logs(
    limit: int = Query(20, ge=1, le=200),
    date_from: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(CardioLog).where(CardioLog.user_id == current_user.id)
    if date_from:
        query = query.where(CardioLog.log_date >= date_from)
    query = query.order_by(desc(CardioLog.log_date)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/cardio", response_model=CardioLogResponse)
async def create_cardio_log(
    data: CardioLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    log = CardioLog(
        user_id=current_user.id,
        log_date=data.log_date,
        type=data.type,
        duration_min=data.duration_min,
        distance_km=data.distance_km,
        zone=data.zone,
        elevation_m=data.elevation_m,
        notes=data.notes,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


@router.delete("/cardio/{log_id}")
async def delete_cardio_log(
    log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(CardioLog).where(CardioLog.id == log_id, CardioLog.user_id == current_user.id)
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Cardio log not found")
    await db.delete(log)
    return {"detail": "Cardio log deleted"}
