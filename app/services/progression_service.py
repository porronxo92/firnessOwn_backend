"""
Progression service - logic for suggesting weight increases
"""
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workout_log import WorkoutLog


def estimate_1rm(weight: float, reps: int) -> float:
    """Epley formula for estimated 1RM"""
    if reps <= 0 or weight <= 0:
        return 0
    return round(weight * (1 + reps / 30), 1)


async def get_progression_suggestion(
    db: AsyncSession,
    user_id: int,
    exercise_id: int,
    target_rir: str
) -> dict:
    """
    Returns a progression suggestion based on last 2 sessions.

    Rules:
    - If user completed all sets with RIR >= target in last 2 sessions:
      suggest increasing load by 2.5-5kg
    - If user did NOT complete sets (reps < target):
      suggest maintaining current load
    """
    # Get last 2 sessions for this exercise
    query = select(WorkoutLog).where(
        WorkoutLog.user_id == user_id,
        WorkoutLog.exercise_id == exercise_id,
        WorkoutLog.weight_kg.isnot(None)
    ).order_by(desc(WorkoutLog.log_date)).limit(2)

    result = await db.execute(query)
    logs = result.scalars().all()

    if len(logs) < 2:
        return {
            "suggestion": "keep",
            "message": "Necesitas al menos 2 sesiones registradas para recibir sugerencias.",
            "current_weight": float(logs[0].weight_kg) if logs else None
        }

    # Parse target RIR (e.g., "2-3" → min = 2)
    try:
        target_min_rir = int(target_rir.split("-")[0])
    except (ValueError, IndexError):
        target_min_rir = 2

    # Check if both sessions had RIR >= target
    all_completed = True
    for log in logs:
        if log.rir_actual:
            try:
                actual_rir = int(log.rir_actual.split("-")[0])
                if actual_rir < target_min_rir:
                    all_completed = False
                    break
            except (ValueError, IndexError):
                pass

    current_weight = float(logs[0].weight_kg)

    if all_completed:
        increase = 2.5 if current_weight < 60 else 5.0
        return {
            "suggestion": "increase",
            "message": f"¡Sube la carga {increase}kg la próxima sesión!",
            "current_weight": current_weight,
            "suggested_weight": current_weight + increase
        }
    else:
        return {
            "suggestion": "maintain",
            "message": "Consolida la carga actual antes de subir.",
            "current_weight": current_weight,
            "suggested_weight": current_weight
        }
