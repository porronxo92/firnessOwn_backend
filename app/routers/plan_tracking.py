from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timezone

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.generated_plan import GeneratedPlan, WeeklyProgress
from app.models.plan_tracking import PlanWeek, PlanDay, PlanExercise, ExerciseLog
from app.schemas.plan_tracking import (
    PlanWeekResponse, PlanWeekWithDays, PlanWeekDetail,
    PlanDayResponse, PlanDayWithExercises,
    PlanExerciseResponse, PlanExerciseWithLogs,
    ExerciseLogCreate, ExerciseLogUpdate, ExerciseLogResponse,
    ExerciseProgression, ExerciseProgressionPoint,
    PlanProgressSummary,
    CompleteDayRequest, CompleteWeekRequest,
)

router = APIRouter()


# === Helper: verificar que el plan pertenece al usuario ===

async def get_user_plan(plan_id: int, user: User, db: AsyncSession) -> GeneratedPlan:
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalars().first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan


# === POPULATE: Explotar JSON en tablas normalizadas ===

@router.post("/plans/{plan_id}/populate", status_code=201)
async def populate_plan_structure(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Explota el plan_structure JSON en tablas normalizadas (plan_weeks, plan_days, plan_exercises).
    Idempotente: si ya existe, no hace nada.
    """
    plan = await get_user_plan(plan_id, current_user, db)

    # Verificar si ya está populado
    result = await db.execute(
        select(func.count(PlanWeek.id)).where(PlanWeek.plan_id == plan_id)
    )
    existing_count = result.scalar() or 0
    if existing_count > 0:
        return {"message": "Plan ya está populado", "weeks_count": existing_count}

    plan_structure = plan.plan_structure
    if not plan_structure:
        raise HTTPException(status_code=400, detail="El plan no tiene estructura definida")

    weeks_data = plan_structure.get("weeks", [])
    phases_data = plan_structure.get("phases", [])
    total_weeks = plan_structure.get("total_weeks", plan.total_weeks)

    # Mapear phase por week_number
    week_to_phase = {}
    for phase in phases_data:
        phase_weeks = phase.get("weeks", [])
        for wn in phase_weeks:
            week_to_phase[wn] = phase.get("name", "")

    # Crear semanas — una por cada semana del plan
    # El JSON solo tiene semanas representativas, las demás repiten el patrón de su fase
    representative_weeks = {w.get("week_number"): w for w in weeks_data}

    try:
        weeks_created = 0
        for week_num in range(1, total_weeks + 1):
            phase_name = week_to_phase.get(week_num, "")

            # Buscar la semana representativa de esta fase
            week_data = representative_weeks.get(week_num)
            if not week_data:
                # Usar la representativa de la misma fase
                for rw in weeks_data:
                    if rw.get("phase") == phase_name:
                        week_data = rw
                        break

            is_deload = week_data.get("is_deload", False) if week_data else False
            focus = week_data.get("focus", "") if week_data else ""
            progression_notes = week_data.get("progression_notes", "") if week_data else ""

            plan_week = PlanWeek(
                plan_id=plan_id,
                week_number=week_num,
                phase_name=phase_name,
                is_deload=is_deload,
                focus=focus,
                progression_notes=progression_notes,
                status="pending"
            )
            db.add(plan_week)
            await db.flush()  # get ID

            # Crear días para esta semana
            days_data = week_data.get("days", []) if week_data else []
            for day_data in days_data:
                cardio = day_data.get("cardio") or {}
                plan_day = PlanDay(
                    week_id=plan_week.id,
                    day_number=day_data.get("day_number", 1),
                    day_name=day_data.get("day_name", ""),
                    type=day_data.get("type", "rest"),
                    session_name=day_data.get("session_name", ""),
                    duration_minutes=day_data.get("duration_minutes"),
                    session_notes=day_data.get("session_notes", ""),
                    cardio_type=cardio.get("type"),
                    cardio_duration_min=cardio.get("duration_minutes"),
                    cardio_intensity=cardio.get("intensity"),
                    cardio_distance_km=cardio.get("distance_km"),
                    cardio_notes=cardio.get("notes"),
                status="pending"
            )
            db.add(plan_day)
            await db.flush()

            # Crear ejercicios para este día
            exercises_data = day_data.get("exercises", [])
            for idx, ex_data in enumerate(exercises_data):
                alternatives = ex_data.get("alternatives", [])
                alt_str = ", ".join(alternatives) if isinstance(alternatives, list) else str(alternatives or "")

                plan_exercise = PlanExercise(
                    day_id=plan_day.id,
                    name=ex_data.get("name", ""),
                    muscle_group=ex_data.get("muscle_group"),
                    sets=ex_data.get("sets", 3),
                    reps=str(ex_data.get("reps", "10")),
                    rir=ex_data.get("rir"),
                    rest_seconds=ex_data.get("rest_seconds"),
                    tempo=ex_data.get("tempo"),
                    notes=ex_data.get("notes"),
                    alternatives=alt_str if alt_str else None,
                    sort_order=idx
                )
                db.add(plan_exercise)

        weeks_created += 1

        await db.commit()

        # Marcar la primera semana como in_progress
        result = await db.execute(
            select(PlanWeek)
            .where(PlanWeek.plan_id == plan_id)
            .where(PlanWeek.week_number == plan.current_week)
        )
        current_plan_week = result.scalars().first()
        if current_plan_week:
            current_plan_week.status = "in_progress"
            current_plan_week.started_at = datetime.now(timezone.utc)
            await db.commit()

        return {"message": "Plan populado correctamente", "weeks_created": weeks_created}

    except IntegrityError:
        # Plan was populated by another request (race condition) or data already exists
        await db.rollback()
        result = await db.execute(
            select(func.count(PlanWeek.id)).where(PlanWeek.plan_id == plan_id)
        )
        existing_count = result.scalar() or 0
        return {"message": "Plan ya está populado", "weeks_count": existing_count}
# === GET WEEKS ===

@router.get("/plans/{plan_id}/weeks", response_model=List[PlanWeekResponse])
async def get_plan_weeks(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista todas las semanas del plan con su status"""
    await get_user_plan(plan_id, current_user, db)

    result = await db.execute(
        select(PlanWeek)
        .where(PlanWeek.plan_id == plan_id)
        .order_by(PlanWeek.week_number)
    )
    return result.scalars().all()


# === GET DAYS OF A WEEK ===

@router.get("/plans/{plan_id}/weeks/{week_number}/days", response_model=List[PlanDayResponse])
async def get_week_days(
    plan_id: int,
    week_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Lista los días de una semana específica"""
    await get_user_plan(plan_id, current_user, db)

    result = await db.execute(
        select(PlanWeek)
        .where(PlanWeek.plan_id == plan_id)
        .where(PlanWeek.week_number == week_number)
    )
    week = result.scalars().first()
    if not week:
        raise HTTPException(status_code=404, detail="Semana no encontrada")

    result = await db.execute(
        select(PlanDay)
        .where(PlanDay.week_id == week.id)
        .order_by(PlanDay.day_number)
    )
    return result.scalars().all()


# === GET DAY DETAIL (with exercises and logs) ===

@router.get("/plan-days/{day_id}", response_model=PlanDayWithExercises)
async def get_day_detail(
    day_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el detalle de un día con ejercicios y sus logs"""
    # Verificar ownership
    result = await db.execute(
        select(PlanDay)
        .where(PlanDay.id == day_id)
    )
    day = result.scalars().first()
    if not day:
        raise HTTPException(status_code=404, detail="Día no encontrado")

    # Verify ownership through chain
    result = await db.execute(
        select(PlanWeek).where(PlanWeek.id == day.week_id)
    )
    week = result.scalars().first()
    await get_user_plan(week.plan_id, current_user, db)

    # Get exercises
    result = await db.execute(
        select(PlanExercise)
        .where(PlanExercise.day_id == day_id)
        .order_by(PlanExercise.sort_order)
    )
    exercises = result.scalars().all()

    # Build response with logs
    exercises_with_logs = []
    for ex in exercises:
        result = await db.execute(
            select(ExerciseLog)
            .where(ExerciseLog.plan_exercise_id == ex.id)
            .order_by(ExerciseLog.set_number)
        )
        logs = result.scalars().all()

        # Calculate best and last weight
        best_weight = None
        last_weight = None
        if logs:
            weights = [l.weight_kg for l in logs if l.weight_kg is not None]
            if weights:
                best_weight = float(max(weights))
                last_weight = float(weights[-1])

        exercises_with_logs.append(PlanExerciseWithLogs(
            id=ex.id,
            day_id=ex.day_id,
            name=ex.name,
            muscle_group=ex.muscle_group,
            sets=ex.sets,
            reps=ex.reps,
            rir=ex.rir,
            rest_seconds=ex.rest_seconds,
            tempo=ex.tempo,
            notes=ex.notes,
            alternatives=ex.alternatives,
            sort_order=ex.sort_order,
            logs=[ExerciseLogResponse.model_validate(l) for l in logs],
            best_weight=best_weight,
            last_weight=last_weight,
        ))

    return PlanDayWithExercises(
        id=day.id,
        week_id=day.week_id,
        day_number=day.day_number,
        day_name=day.day_name,
        type=day.type,
        session_name=day.session_name,
        duration_minutes=day.duration_minutes,
        session_notes=day.session_notes,
        cardio_type=day.cardio_type,
        cardio_duration_min=day.cardio_duration_min,
        cardio_intensity=day.cardio_intensity,
        cardio_distance_km=float(day.cardio_distance_km) if day.cardio_distance_km else None,
        cardio_notes=day.cardio_notes,
        status=day.status,
        completed_at=day.completed_at,
        exercises=exercises_with_logs,
    )


# === LOG AN EXERCISE SET ===

@router.post("/plan-exercises/{exercise_id}/log", response_model=ExerciseLogResponse, status_code=201)
async def log_exercise_set(
    exercise_id: int,
    log_data: ExerciseLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registra una serie de un ejercicio"""
    # Verify exercise exists and user owns it
    result = await db.execute(
        select(PlanExercise).where(PlanExercise.id == exercise_id)
    )
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    # Verify ownership
    result = await db.execute(select(PlanDay).where(PlanDay.id == exercise.day_id))
    day = result.scalars().first()
    result = await db.execute(select(PlanWeek).where(PlanWeek.id == day.week_id))
    week = result.scalars().first()
    await get_user_plan(week.plan_id, current_user, db)

    # Create log
    new_log = ExerciseLog(
        plan_exercise_id=exercise_id,
        user_id=current_user.id,
        set_number=log_data.set_number,
        weight_kg=log_data.weight_kg,
        reps_done=log_data.reps_done,
        rir_actual=log_data.rir_actual,
        rpe=log_data.rpe,
        completed=log_data.completed,
        notes=log_data.notes,
    )
    db.add(new_log)
    await db.commit()
    await db.refresh(new_log)

    return new_log


# === BATCH LOG (multiple sets at once) ===

@router.post("/plan-exercises/{exercise_id}/log-batch", response_model=List[ExerciseLogResponse], status_code=201)
async def log_exercise_batch(
    exercise_id: int,
    logs_data: List[ExerciseLogCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Registra múltiples series de un ejercicio de una vez"""
    # Verify exercise exists and user owns it
    result = await db.execute(
        select(PlanExercise).where(PlanExercise.id == exercise_id)
    )
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")

    result = await db.execute(select(PlanDay).where(PlanDay.id == exercise.day_id))
    day = result.scalars().first()
    result = await db.execute(select(PlanWeek).where(PlanWeek.id == day.week_id))
    week = result.scalars().first()
    await get_user_plan(week.plan_id, current_user, db)

    # Delete existing logs for this exercise (replace mode)
    existing = await db.execute(
        select(ExerciseLog).where(ExerciseLog.plan_exercise_id == exercise_id)
    )
    for old_log in existing.scalars().all():
        await db.delete(old_log)

    # Create new logs
    created = []
    for log_data in logs_data:
        new_log = ExerciseLog(
            plan_exercise_id=exercise_id,
            user_id=current_user.id,
            set_number=log_data.set_number,
            weight_kg=log_data.weight_kg,
            reps_done=log_data.reps_done,
            rir_actual=log_data.rir_actual,
            rpe=log_data.rpe,
            completed=log_data.completed,
            notes=log_data.notes,
        )
        db.add(new_log)
        created.append(new_log)

    await db.commit()
    for log in created:
        await db.refresh(log)

    return created


# === UPDATE LOG ===

@router.put("/exercise-logs/{log_id}", response_model=ExerciseLogResponse)
async def update_exercise_log(
    log_id: int,
    update_data: ExerciseLogUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Edita un log de ejercicio"""
    result = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.id == log_id)
        .where(ExerciseLog.user_id == current_user.id)
    )
    log = result.scalars().first()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")

    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(log, field, value)

    await db.commit()
    await db.refresh(log)
    return log


# === DELETE LOG ===

@router.delete("/exercise-logs/{log_id}", status_code=204)
async def delete_exercise_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Elimina un log de ejercicio"""
    result = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.id == log_id)
        .where(ExerciseLog.user_id == current_user.id)
    )
    log = result.scalars().first()
    if not log:
        raise HTTPException(status_code=404, detail="Log no encontrado")

    await db.delete(log)
    await db.commit()


# === COMPLETE DAY ===

@router.post("/plan-days/{day_id}/complete", response_model=PlanDayResponse)
async def complete_day(
    day_id: int,
    request: CompleteDayRequest = CompleteDayRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marca un día como completado"""
    result = await db.execute(select(PlanDay).where(PlanDay.id == day_id))
    day = result.scalars().first()
    if not day:
        raise HTTPException(status_code=404, detail="Día no encontrado")

    # Verify ownership
    result = await db.execute(select(PlanWeek).where(PlanWeek.id == day.week_id))
    week = result.scalars().first()
    await get_user_plan(week.plan_id, current_user, db)

    day.status = "completed"
    day.completed_at = datetime.now(timezone.utc)
    if request.notes:
        day.session_notes = (day.session_notes or "") + f"\n[Usuario]: {request.notes}"

    # Update weekly progress sessions_completed
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == week.plan_id)
        .where(WeeklyProgress.week_number == week.week_number)
    )
    weekly_progress = result.scalars().first()
    if weekly_progress:
        weekly_progress.sessions_completed = (weekly_progress.sessions_completed or 0) + 1

    await db.commit()
    await db.refresh(day)
    return day


# === COMPLETE WEEK ===

@router.post("/plan-weeks/{week_id}/complete", response_model=PlanWeekResponse)
async def complete_week(
    week_id: int,
    request: CompleteWeekRequest = CompleteWeekRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marca una semana como completada y avanza a la siguiente"""
    result = await db.execute(select(PlanWeek).where(PlanWeek.id == week_id))
    week = result.scalars().first()
    if not week:
        raise HTTPException(status_code=404, detail="Semana no encontrada")

    plan = await get_user_plan(week.plan_id, current_user, db)

    week.status = "completed"
    week.completed_at = datetime.now(timezone.utc)

    # Update weekly progress feedback
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == plan.id)
        .where(WeeklyProgress.week_number == week.week_number)
    )
    weekly_progress = result.scalars().first()
    if weekly_progress:
        weekly_progress.completed_at = datetime.now(timezone.utc)
        if request.energy_level:
            weekly_progress.energy_level = request.energy_level
        if request.soreness_level:
            weekly_progress.soreness_level = request.soreness_level
        if request.motivation_level:
            weekly_progress.motivation_level = request.motivation_level
        if request.notes:
            weekly_progress.user_notes = request.notes

    # Advance to next week
    next_week_number = week.week_number + 1
    if next_week_number <= plan.total_weeks:
        plan.current_week = next_week_number

        # Mark next week as in_progress
        result = await db.execute(
            select(PlanWeek)
            .where(PlanWeek.plan_id == plan.id)
            .where(PlanWeek.week_number == next_week_number)
        )
        next_week = result.scalars().first()
        if next_week:
            next_week.status = "in_progress"
            next_week.started_at = datetime.now(timezone.utc)
    else:
        # Plan completado
        plan.completed_at = datetime.now(timezone.utc)
        plan.is_active = False

    await db.commit()
    await db.refresh(week)
    return week


# === PROGRESSION ===

@router.get("/plans/{plan_id}/progression")
async def get_exercise_progression(
    plan_id: int,
    exercise_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene la progresión de ejercicios del plan.
    Si se pasa exercise_name, filtra por ese ejercicio.
    Si no, devuelve todos los ejercicios que tienen logs.
    """
    await get_user_plan(plan_id, current_user, db)

    # Get all plan exercises with their logs, grouped by name and week
    query = (
        select(
            PlanExercise.name,
            PlanWeek.week_number,
            PlanWeek.phase_name,
            func.max(ExerciseLog.weight_kg).label("max_weight"),
            func.avg(ExerciseLog.weight_kg).label("avg_weight"),
            func.max(ExerciseLog.reps_done).label("max_reps"),
            func.avg(ExerciseLog.reps_done).label("avg_reps"),
            func.count(ExerciseLog.id).label("total_sets"),
        )
        .join(PlanDay, PlanDay.id == PlanExercise.day_id)
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .join(ExerciseLog, ExerciseLog.plan_exercise_id == PlanExercise.id)
        .where(PlanWeek.plan_id == plan_id)
    )

    if exercise_name:
        query = query.where(PlanExercise.name.ilike(f"%{exercise_name}%"))

    query = query.group_by(
        PlanExercise.name,
        PlanWeek.week_number,
        PlanWeek.phase_name,
    ).order_by(PlanExercise.name, PlanWeek.week_number)

    result = await db.execute(query)
    rows = result.all()

    # Group by exercise name
    progressions = {}
    for row in rows:
        name = row.name
        if name not in progressions:
            progressions[name] = {
                "exercise_name": name,
                "plan_id": plan_id,
                "points": [],
                "best_weight_ever": 0,
                "best_1rm_ever": 0,
            }

        max_w = float(row.max_weight) if row.max_weight else 0
        max_r = int(row.max_reps) if row.max_reps else 0
        estimated_1rm = max_w * (1 + max_r / 30) if max_w and max_r else 0

        progressions[name]["points"].append({
            "week_number": row.week_number,
            "phase_name": row.phase_name,
            "max_weight": float(row.max_weight) if row.max_weight else None,
            "avg_weight": round(float(row.avg_weight), 2) if row.avg_weight else None,
            "max_reps": int(row.max_reps) if row.max_reps else None,
            "avg_reps": round(float(row.avg_reps), 1) if row.avg_reps else None,
            "total_sets_logged": row.total_sets,
            "estimated_1rm": round(estimated_1rm, 2) if estimated_1rm else None,
        })

        if max_w > progressions[name]["best_weight_ever"]:
            progressions[name]["best_weight_ever"] = max_w
        if estimated_1rm > progressions[name]["best_1rm_ever"]:
            progressions[name]["best_1rm_ever"] = round(estimated_1rm, 2)

    # Calculate trend for each exercise
    for name, data in progressions.items():
        points = data["points"]
        if len(points) >= 2:
            first_weight = points[0]["max_weight"] or 0
            last_weight = points[-1]["max_weight"] or 0
            if last_weight > first_weight:
                data["trend"] = "up"
            elif last_weight < first_weight:
                data["trend"] = "down"
            else:
                data["trend"] = "stable"
        else:
            data["trend"] = "stable"

    return list(progressions.values())


# === PLAN PROGRESS SUMMARY ===

@router.get("/plans/{plan_id}/summary", response_model=PlanProgressSummary)
async def get_plan_summary(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resumen de progreso del plan"""
    plan = await get_user_plan(plan_id, current_user, db)

    # Weeks
    result = await db.execute(
        select(func.count(PlanWeek.id)).where(PlanWeek.plan_id == plan_id)
    )
    total_weeks = result.scalar() or 0

    result = await db.execute(
        select(func.count(PlanWeek.id))
        .where(PlanWeek.plan_id == plan_id)
        .where(PlanWeek.status == "completed")
    )
    weeks_completed = result.scalar() or 0

    # Days
    result = await db.execute(
        select(func.count(PlanDay.id))
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
        .where(PlanDay.type != "rest")
    )
    total_days = result.scalar() or 0

    result = await db.execute(
        select(func.count(PlanDay.id))
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
        .where(PlanDay.status == "completed")
    )
    days_completed = result.scalar() or 0

    # Exercises and logs
    result = await db.execute(
        select(func.count(PlanExercise.id))
        .join(PlanDay, PlanDay.id == PlanExercise.day_id)
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
    )
    total_exercises = result.scalar() or 0

    result = await db.execute(
        select(func.count(ExerciseLog.id))
        .join(PlanExercise, PlanExercise.id == ExerciseLog.plan_exercise_id)
        .join(PlanDay, PlanDay.id == PlanExercise.day_id)
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
    )
    total_sets_logged = result.scalar() or 0

    result = await db.execute(
        select(func.count(func.distinct(PlanExercise.name)))
        .join(PlanDay, PlanDay.id == PlanExercise.day_id)
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
    )
    unique_exercises = result.scalar() or 0

    completion_percent = (days_completed / total_days * 100) if total_days > 0 else 0

    return PlanProgressSummary(
        plan_id=plan_id,
        total_weeks=total_weeks,
        weeks_completed=weeks_completed,
        total_days=total_days,
        days_completed=days_completed,
        total_exercises=total_exercises,
        total_sets_logged=total_sets_logged,
        unique_exercises=unique_exercises,
        completion_percent=round(completion_percent, 1),
    )


# === GET EXERCISE HISTORY (for a specific plan_exercise) ===

@router.get("/plan-exercises/{exercise_id}/logs", response_model=List[ExerciseLogResponse])
async def get_exercise_logs(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los logs de un ejercicio específico"""
    result = await db.execute(
        select(ExerciseLog)
        .where(ExerciseLog.plan_exercise_id == exercise_id)
        .where(ExerciseLog.user_id == current_user.id)
        .order_by(ExerciseLog.set_number)
    )
    return result.scalars().all()


# === GET PREVIOUS LOGS for same exercise name (cross-week) ===

@router.get("/plans/{plan_id}/exercise-history/{exercise_name}")
async def get_exercise_name_history(
    plan_id: int,
    exercise_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene el historial de un ejercicio por nombre a través de todas las semanas.
    Útil para ver qué se hizo la última vez en el mismo ejercicio.
    """
    await get_user_plan(plan_id, current_user, db)

    result = await db.execute(
        select(
            PlanWeek.week_number,
            PlanDay.day_name,
            ExerciseLog.set_number,
            ExerciseLog.weight_kg,
            ExerciseLog.reps_done,
            ExerciseLog.rir_actual,
            ExerciseLog.rpe,
            ExerciseLog.created_at,
        )
        .join(PlanExercise, PlanExercise.id == ExerciseLog.plan_exercise_id)
        # === exercise-history join continues below ===
        .join(PlanDay, PlanDay.id == PlanExercise.day_id)
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
        .where(PlanExercise.name.ilike(f"%{exercise_name}%"))
        .where(ExerciseLog.user_id == current_user.id)
        .order_by(PlanWeek.week_number, ExerciseLog.set_number)
    )
    rows = result.all()

    history = []
    for row in rows:
        history.append({
            "week_number": row.week_number,
            "day_name": row.day_name,
            "set_number": row.set_number,
            "weight_kg": float(row.weight_kg) if row.weight_kg else None,
            "reps_done": row.reps_done,
            "rir_actual": row.rir_actual,
            "rpe": float(row.rpe) if row.rpe else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        })

    return history


# === GET ALL RECENT EXERCISE LOGS (for Registro view) ===

@router.get("/plans/{plan_id}/recent-logs")
async def get_plan_recent_logs(
    plan_id: int,
    limit: int = Query(200, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve todos los registros de ejercicio del plan, agrupados por ejercicio
    (plan_exercise_id), con los datos agregados de cada serie.
    Ordenado por fecha descendente. Para la vista Registro.
    """
    await get_user_plan(plan_id, current_user, db)

    query = (
        select(
            ExerciseLog.plan_exercise_id,
            PlanExercise.name.label("exercise_name"),
            PlanExercise.muscle_group,
            PlanDay.type.label("day_type"),
            PlanDay.session_name,
            PlanDay.day_name,
            PlanWeek.week_number,
            PlanWeek.phase_name,
            func.count(ExerciseLog.id).label("sets_done"),
            func.max(ExerciseLog.weight_kg).label("max_weight_kg"),
            func.max(ExerciseLog.reps_done).label("max_reps_done"),
            func.max(ExerciseLog.rir_actual).label("rir_actual"),
            func.max(ExerciseLog.created_at).label("last_set_at"),
        )
        .join(PlanExercise, PlanExercise.id == ExerciseLog.plan_exercise_id)
        .join(PlanDay, PlanDay.id == PlanExercise.day_id)
        .join(PlanWeek, PlanWeek.id == PlanDay.week_id)
        .where(PlanWeek.plan_id == plan_id)
        .where(ExerciseLog.user_id == current_user.id)
        .group_by(
            ExerciseLog.plan_exercise_id,
            PlanExercise.name,
            PlanExercise.muscle_group,
            PlanDay.type,
            PlanDay.session_name,
            PlanDay.day_name,
            PlanWeek.week_number,
            PlanWeek.phase_name,
        )
        .order_by(func.max(ExerciseLog.created_at).desc())
        .limit(limit)
    )

    result = await db.execute(query)
    rows = result.all()

    logs = []
    for row in rows:
        last_set_at = row.last_set_at
        log_date = last_set_at.date().isoformat() if last_set_at else None
        logs.append({
            "plan_exercise_id": row.plan_exercise_id,
            "exercise_name": row.exercise_name,
            "muscle_group": row.muscle_group,
            "day_type": row.day_type,
            "session_name": row.session_name,
            "day_name": row.day_name,
            "week_number": row.week_number,
            "phase_name": row.phase_name,
            "sets_done": row.sets_done,
            "max_weight_kg": float(row.max_weight_kg) if row.max_weight_kg else None,
            "max_reps_done": row.max_reps_done,
            "rir_actual": row.rir_actual,
            "last_set_at": last_set_at.isoformat() if last_set_at else None,
            "log_date": log_date,
        })

    return logs
