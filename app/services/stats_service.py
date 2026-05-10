"""
Stats service - helper functions for statistics calculations
"""
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workout_log import WorkoutLog
from app.models.exercise import Exercise


def estimate_1rm(weight: float, reps: int) -> float:
    """Epley formula"""
    if reps <= 0 or weight <= 0:
        return 0.0
    return round(weight * (1 + reps / 30), 1)


async def get_exercise_trend(db: AsyncSession, user_id: int, exercise_id: int, limit: int = 10) -> str:
    """Determine if exercise weight is trending up, down, or stable"""
    query = select(WorkoutLog.weight_kg).where(
        WorkoutLog.user_id == user_id,
        WorkoutLog.exercise_id == exercise_id,
        WorkoutLog.weight_kg.isnot(None)
    ).order_by(desc(WorkoutLog.log_date)).limit(limit)

    result = await db.execute(query)
    weights = [float(row[0]) for row in result.all()]

    if len(weights) < 2:
        return "stable"

    first = weights[-1]  # oldest
    last = weights[0]    # newest
    delta = last - first

    if delta > 2:
        return "up"
    elif delta < -2:
        return "down"
    return "stable"
