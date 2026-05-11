import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from typing import Optional
import asyncio
import httpx

logger = logging.getLogger(__name__)

from app.database import get_db, async_session
from app.auth import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.generated_plan import GeneratedPlan, WeeklyProgress
from app.models.plan_tracking import PlanWeek, PlanDay, PlanExercise
from app.schemas.user_profile import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    OnboardingStep1, OnboardingStep2, OnboardingStep3,
    OnboardingStep4, OnboardingStep5, OnboardingStep6
)
from app.schemas.generated_plan import (
    GeneratedPlanResponse, GeneratedPlanSummary, PlanGenerationAccepted, PlanGenerationStatus,
    WeeklyProgressCreate, WeeklyProgressUpdate, WeeklyProgressResponse,
    GeneratePlanRequest, AdjustmentFeedback, AdjustmentSuggestionResponse,
    CurrentWeekResponse, WeekPlan
)
from app.services.gemini_service import gemini_service

router = APIRouter()


# === Endpoints de Perfil de Usuario ===

@router.get("/profile", response_model=Optional[UserProfileResponse])
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el perfil del usuario actual"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    return profile


@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Crea el perfil del usuario (se usa al completar el onboarding)"""
    # Verificar si ya existe un perfil
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    existing_profile = result.scalar_one_or_none()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya tiene un perfil. Usa PUT para actualizarlo."
        )
    
    # Crear el perfil
    profile = UserProfile(
        user_id=current_user.id,
        **profile_data.model_dump(exclude_unset=True)
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.put("/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el perfil del usuario"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado. Usa POST para crearlo."
        )
    
    # Actualizar campos
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


# === Endpoints de Onboarding por pasos ===

@router.post("/step1", response_model=UserProfileResponse)
async def onboarding_step1(
    step_data: OnboardingStep1,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Paso 1 del onboarding: Datos físicos básicos"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)
    
    # Actualizar datos del paso 1
    for field, value in step_data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/step2", response_model=UserProfileResponse)
async def onboarding_step2(
    step_data: OnboardingStep2,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Paso 2 del onboarding: Objetivos"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa el paso 1 primero"
        )
    
    for field, value in step_data.model_dump(exclude_unset=True).items():
        if field == "primary_goal" and value:
            setattr(profile, field, value.value if hasattr(value, 'value') else value)
        elif field == "secondary_goals" and value:
            setattr(profile, field, [g.value if hasattr(g, 'value') else g for g in value])
        else:
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/step3", response_model=UserProfileResponse)
async def onboarding_step3(
    step_data: OnboardingStep3,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Paso 3 del onboarding: Disponibilidad y periodo"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa los pasos anteriores primero"
        )
    
    for field, value in step_data.model_dump(exclude_unset=True).items():
        if field == "training_period" and value:
            setattr(profile, field, value.value if hasattr(value, 'value') else value)
        else:
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/step4", response_model=UserProfileResponse)
async def onboarding_step4(
    step_data: OnboardingStep4,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Paso 4 del onboarding: Recursos disponibles"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa los pasos anteriores primero"
        )
    
    for field, value in step_data.model_dump(exclude_unset=True).items():
        if field == "bike_type" and value:
            setattr(profile, field, value.value if hasattr(value, 'value') else value)
        else:
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/step5", response_model=UserProfileResponse)
async def onboarding_step5(
    step_data: OnboardingStep5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Paso 5 del onboarding: Experiencia y salud"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa los pasos anteriores primero"
        )
    
    for field, value in step_data.model_dump(exclude_unset=True).items():
        if field == "fitness_level" and value:
            setattr(profile, field, value.value if hasattr(value, 'value') else value)
        else:
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/step6", response_model=UserProfileResponse)
async def onboarding_step6(
    step_data: OnboardingStep6,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Paso 6 del onboarding: Alimentación y preferencias"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa los pasos anteriores primero"
        )
    
    for field, value in step_data.model_dump(exclude_unset=True).items():
        if field == "diet_type" and value:
            setattr(profile, field, value.value if hasattr(value, 'value') else value)
        else:
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


@router.post("/complete", response_model=UserProfileResponse)
async def complete_onboarding(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Marca el onboarding como completado"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Perfil no encontrado. Completa todos los pasos del onboarding."
        )
    
    # Validar que hay suficiente información
    if not profile.primary_goal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes especificar al menos un objetivo principal"
        )
    
    if not profile.training_days_per_week:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes especificar los días de entrenamiento por semana"
        )
    
    # Marcar como completado
    profile.onboarding_completed = True
    profile.onboarding_completed_at = datetime.now(timezone.utc)
    
    # Actualizar también el flag en el usuario
    current_user.onboarding_completed = True
    
    await db.commit()
    await db.refresh(profile)
    
    return profile


# === Background task: generación asíncrona con Gemini ===

async def _run_plan_generation_background(plan_id: int, profile_dict: dict, primary_goal: str):
    """
    Tarea de fondo que llama a Gemini y persiste el plan completo.
    Abre su propia sesión de BD para no depender del ciclo de vida del request.
    """
    goal_to_plan_type = {
        "hypertrophy": "strength",
        "strength": "strength",
        "bodyweight": "bodyweight",
        "marathon": "running",
        "half_marathon": "running",
        "endurance": "hybrid",
        "weight_loss": "hybrid",
        "general_fitness": "hybrid"
    }

    async with async_session() as session:
        try:
            # Llamar a Gemini (puede tardar varios minutos)
            generation_result = await gemini_service.generate_training_plan(profile_dict)
            plan_structure = generation_result["plan"]

            # Normalizar la respuesta de Gemini para asegurar compatibilidad
            if "representative_weeks" in plan_structure and "weeks" not in plan_structure:
                plan_structure["weeks"] = plan_structure.pop("representative_weeks")
            for week in plan_structure.get("weeks", []):
                if "week_example" in week and "week_number" not in week:
                    week["week_number"] = week.pop("week_example")
            for phase in plan_structure.get("phases", []):
                if "weeks_range" in phase and "weeks" not in phase:
                    wr = phase.pop("weeks_range")
                    if isinstance(wr, list) and len(wr) == 2:
                        phase["weeks"] = list(range(wr[0], wr[1] + 1))
                    else:
                        phase["weeks"] = wr

            plan_type = goal_to_plan_type.get(primary_goal, "hybrid")

            # Actualizar el plan placeholder con los datos reales
            result = await session.execute(
                select(GeneratedPlan).where(GeneratedPlan.id == plan_id)
            )
            plan = result.scalar_one()
            plan.name = plan_structure.get("plan_name", f"Plan de {primary_goal}")
            plan.description = plan_structure.get("overview", "")
            plan.total_weeks = plan_structure.get("total_weeks", 16)
            plan.plan_type = plan_type
            plan.plan_structure = plan_structure
            plan.gemini_prompt_used = generation_result.get("prompt_used")
            plan.gemini_model_version = generation_result.get("model_version")
            plan.generation_status = "completed"
            await session.commit()
            await session.refresh(plan)

            # Crear entradas de progreso semanal
            for week_num in range(1, plan.total_weeks + 1):
                week_data = next(
                    (w for w in plan_structure.get("weeks", []) if w.get("week_number") == week_num),
                    {}
                )
                days = week_data.get("days", [])
                sessions_planned = sum(
                    1 for d in days if d.get("type") not in ["rest", "active_recovery"]
                )
                session.add(WeeklyProgress(
                    plan_id=plan.id,
                    week_number=week_num,
                    sessions_planned=sessions_planned,
                    sessions_completed=0
                ))
            await session.commit()
            await session.refresh(plan)

            # Poblar tablas normalizadas de tracking
            await _populate_plan_tracking(session, plan, plan_structure)

        except Exception as e:
            logger.exception("Error generando plan id=%s", plan_id)
            # Marcar el plan como error en una sesión nueva para evitar estado sucio
            async with async_session() as err_session:
                result = await err_session.execute(
                    select(GeneratedPlan).where(GeneratedPlan.id == plan_id)
                )
                plan = result.scalar_one_or_none()
                if plan:
                    plan.generation_status = "error"
                    plan.generation_error = "Error interno al generar el plan"
                    await err_session.commit()


# === Endpoints de Generación de Plan con Gemini ===

@router.post("/generate-plan", response_model=PlanGenerationAccepted, status_code=202)
async def generate_training_plan(
    request: GeneratePlanRequest = GeneratePlanRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lanza la generación del plan con IA en segundo plano y devuelve inmediatamente.
    Usa GET /plans/{plan_id}/generation-status para saber cuándo está listo.
    """
    # Obtener perfil del usuario
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Completa el onboarding antes de generar un plan"
        )

    # Si no quiere regenerar, verificar si ya tiene un plan activo completado
    if not request.regenerate:
        result = await db.execute(
            select(GeneratedPlan)
            .where(GeneratedPlan.user_profile_id == profile.id)
            .where(GeneratedPlan.is_active == True)
            .where(GeneratedPlan.generation_status == "completed")
            .limit(1)
        )
        existing_plan = result.scalars().first()
        if existing_plan:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya tienes un plan activo. Usa regenerate=true para crear uno nuevo."
            )
    else:
        # Desactivar planes existentes
        result = await db.execute(
            select(GeneratedPlan)
            .where(GeneratedPlan.user_profile_id == profile.id)
            .where(GeneratedPlan.is_active == True)
        )
        for plan in result.scalars().all():
            plan.is_active = False

    # Convertir perfil a diccionario para la tarea de fondo
    profile_dict = {
        "age": profile.age,
        "gender": profile.gender,
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "body_fat_percentage": profile.body_fat_percentage,
        "primary_goal": profile.primary_goal,
        "secondary_goals": profile.secondary_goals or [],
        "target_weight_kg": profile.target_weight_kg,
        "training_days_per_week": profile.training_days_per_week,
        "preferred_days": profile.preferred_days or [],
        "session_duration_minutes": profile.session_duration_minutes,
        "training_period": profile.training_period,
        "target_event_date": str(profile.target_event_date) if profile.target_event_date else None,
        "target_event_name": profile.target_event_name,
        "has_gym_access": profile.has_gym_access,
        "has_home_equipment": profile.has_home_equipment,
        "home_equipment_list": profile.home_equipment_list or [],
        "has_bike": profile.has_bike,
        "bike_type": profile.bike_type,
        "has_running_gear": profile.has_running_gear,
        "outdoor_space_available": profile.outdoor_space_available,
        "pool_access": profile.pool_access,
        "fitness_level": profile.fitness_level,
        "years_training": profile.years_training,
        "previous_injuries": profile.previous_injuries,
        "health_conditions": profile.health_conditions,
        "diet_type": profile.diet_type,
        "meals_per_day": profile.meals_per_day,
        "preferred_training_types": profile.preferred_training_types or [],
        "disliked_exercises": profile.disliked_exercises or [],
        "favorite_exercises": profile.favorite_exercises or []
    }

    # Crear plan placeholder con estado 'generating'
    goal_to_plan_type = {
        "hypertrophy": "strength", "strength": "strength", "bodyweight": "bodyweight",
        "marathon": "running", "half_marathon": "running",
        "endurance": "hybrid", "weight_loss": "hybrid", "general_fitness": "hybrid"
    }
    placeholder = GeneratedPlan(
        user_profile_id=profile.id,
        name="Tu plan personalizado (generando...)",
        description="",
        total_weeks=16,
        plan_type=goal_to_plan_type.get(profile.primary_goal, "hybrid"),
        primary_focus=profile.primary_goal,
        plan_structure={},
        is_active=True,
        started_at=datetime.now(timezone.utc),
        generation_status="generating",
    )
    db.add(placeholder)
    await db.commit()
    await db.refresh(placeholder)
    plan_id = placeholder.id

    # Lanzar la generación en segundo plano (sin bloquear el request)
    asyncio.create_task(
        _run_plan_generation_background(plan_id, profile_dict, profile.primary_goal or "general_fitness")
    )

    return PlanGenerationAccepted(
        plan_id=plan_id,
        status="generating",
        message=(
            "Tu plan personalizado con IA está siendo creado. "
            "Nuestro sistema está analizando tu perfil, objetivos y disponibilidad "
            "para diseñar un programa completamente adaptado a ti. "
            "Esto puede tardar entre 1 y 3 minutos."
        )
    )


@router.get("/plans/{plan_id}/generation-status", response_model=PlanGenerationStatus)
async def get_plan_generation_status(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Consulta el estado de generación de un plan (para polling desde el frontend)."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")

    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")

    return plan


@router.get("/plans", response_model=list[GeneratedPlanSummary])
async def get_user_plans(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene todos los planes del usuario"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        return []
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.user_profile_id == profile.id)
        .order_by(GeneratedPlan.created_at.desc())
    )
    
    return result.scalars().all()


@router.get("/plans/active", response_model=Optional[GeneratedPlanResponse])
async def get_active_plan(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el plan activo del usuario"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        return None
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.user_profile_id == profile.id)
        .where(GeneratedPlan.is_active == True)
        .order_by(GeneratedPlan.created_at.desc())
        .limit(1)
    )
    
    return result.scalars().first()


@router.get("/plans/{plan_id}", response_model=GeneratedPlanResponse)
async def get_plan_by_id(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un plan específico por ID"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    return plan


@router.get("/plans/{plan_id}/current-week")
async def get_current_week(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene los datos de la semana actual del plan"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Obtener datos de la semana actual
    current_week = plan.current_week
    plan_structure = plan.plan_structure
    
    # Buscar la semana exacta, o la semana representativa de la fase correspondiente
    weeks = plan_structure.get("weeks", [])
    week_data = next(
        (w for w in weeks if w.get("week_number") == current_week),
        None
    )
    
    # Si no se encontró semana exacta, buscar la semana representativa de la fase actual
    if not week_data and weeks:
        # Determinar en qué fase estamos
        current_phase = None
        for phase in plan_structure.get("phases", []):
            phase_weeks = phase.get("weeks", [])
            if current_week in phase_weeks:
                current_phase = phase.get("name")
                break
        
        # Buscar la semana representativa de esa fase
        if current_phase:
            week_data = next(
                (w for w in weeks if w.get("phase") == current_phase),
                None
            )
        
        # Si aún no hay, usar la primera semana disponible
        if not week_data:
            week_data = weeks[0] if weeks else None
        
        # Ajustar el week_number para que refleje la semana actual
        if week_data:
            week_data = {**week_data, "week_number": current_week}
    
    if not week_data:
        raise HTTPException(status_code=404, detail="Datos de semana no encontrados")
    
    # Obtener progreso de la semana
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == plan_id)
        .where(WeeklyProgress.week_number == current_week)
    )
    progress = result.scalar_one_or_none()
    
    # Obtener la fase actual
    phase_name = week_data.get("phase", "")
    
    return {
        "plan_id": plan.id,
        "plan_name": plan.name,
        "week_number": current_week,
        "total_weeks": plan.total_weeks,
        "phase_name": phase_name,
        "is_deload": week_data.get("is_deload", False),
        "week_plan": week_data,
        "progress": progress
    }


@router.put("/plans/{plan_id}/advance-week")
async def advance_to_next_week(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Avanza a la siguiente semana del plan"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    if plan.current_week >= plan.total_weeks:
        plan.completed_at = datetime.now(timezone.utc)
        plan.is_active = False
        await db.commit()
        return {"message": "Plan completado", "completed": True}
    
    # Marcar semana actual como completada
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == plan_id)
        .where(WeeklyProgress.week_number == plan.current_week)
    )
    current_progress = result.scalar_one_or_none()
    if current_progress:
        current_progress.completed_at = datetime.now(timezone.utc)
    
    # Avanzar a la siguiente semana
    plan.current_week += 1
    
    # Marcar inicio de nueva semana
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == plan_id)
        .where(WeeklyProgress.week_number == plan.current_week)
    )
    next_progress = result.scalar_one_or_none()
    if next_progress:
        next_progress.started_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return {"message": f"Avanzado a semana {plan.current_week}", "current_week": plan.current_week}


# === Endpoints de Progreso Semanal ===

@router.get("/plans/{plan_id}/progress", response_model=list[WeeklyProgressResponse])
async def get_plan_progress(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el progreso de todas las semanas de un plan"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == plan_id)
        .order_by(WeeklyProgress.week_number)
    )
    
    return result.scalars().all()


@router.put("/plans/{plan_id}/progress/{week_number}", response_model=WeeklyProgressResponse)
async def update_weekly_progress(
    plan_id: int,
    week_number: int,
    progress_data: WeeklyProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Actualiza el progreso de una semana específica"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    result = await db.execute(
        select(WeeklyProgress)
        .where(WeeklyProgress.plan_id == plan_id)
        .where(WeeklyProgress.week_number == week_number)
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")
    
    # Actualizar campos
    for field, value in progress_data.model_dump(exclude_unset=True).items():
        setattr(progress, field, value)
    
    await db.commit()
    await db.refresh(progress)
    
    return progress


@router.post("/plans/{plan_id}/progress/{week_number}/get-suggestions", response_model=AdjustmentSuggestionResponse)
async def get_adjustment_suggestions(
    plan_id: int,
    week_number: int,
    feedback: AdjustmentFeedback,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene sugerencias de ajuste de Gemini basadas en el feedback semanal"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Perfil no encontrado")
    
    result = await db.execute(
        select(GeneratedPlan)
        .where(GeneratedPlan.id == plan_id)
        .where(GeneratedPlan.user_profile_id == profile.id)
    )
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    try:
        # Obtener sugerencias de Gemini
        feedback_dict = feedback.model_dump()
        suggestions = await gemini_service.get_plan_adjustment_suggestions(
            plan.plan_structure,
            feedback_dict
        )
        
        # Guardar sugerencias en el progreso semanal
        result = await db.execute(
            select(WeeklyProgress)
            .where(WeeklyProgress.plan_id == plan_id)
            .where(WeeklyProgress.week_number == week_number)
        )
        progress = result.scalar_one_or_none()
        
        if progress:
            progress.ai_feedback = suggestions.get("analysis", "")
            progress.suggested_adjustments = suggestions
            progress.energy_level = feedback.energy_level
            progress.soreness_level = feedback.soreness_level
            progress.motivation_level = feedback.motivation_level
            progress.user_notes = feedback.user_notes
            progress.sessions_completed = feedback.sessions_completed
            await db.commit()
        
        return suggestions
        
    except Exception as e:
        logger.exception("Error al obtener sugerencias de progresión")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener sugerencias de progresión"
        )


# === Estado del onboarding ===

@router.get("/status")
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Obtiene el estado del onboarding del usuario"""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    # Determinar pasos completados
    steps_completed = {
        "step1": False,
        "step2": False,
        "step3": False,
        "step4": False,
        "step5": False,
        "step6": False
    }
    
    if profile:
        # Step 1: Datos físicos
        if any([profile.age, profile.gender, profile.height_cm, profile.weight_kg]):
            steps_completed["step1"] = True
        
        # Step 2: Objetivos
        if profile.primary_goal:
            steps_completed["step2"] = True
        
        # Step 3: Disponibilidad
        if profile.training_days_per_week and profile.training_period:
            steps_completed["step3"] = True
        
        # Step 4: Recursos
        if any([profile.has_gym_access, profile.has_home_equipment, profile.has_bike]):
            steps_completed["step4"] = True
        
        # Step 5: Experiencia
        if profile.fitness_level:
            steps_completed["step5"] = True
        
        # Step 6: Alimentación (opcional pero contamos si hay datos)
        if profile.diet_type or profile.preferred_training_types:
            steps_completed["step6"] = True
    
    # Calcular siguiente paso
    next_step = 1
    for i in range(1, 7):
        if not steps_completed[f"step{i}"]:
            next_step = i
            break
    else:
        next_step = 7  # Todos completados
    
    # Comprobar si tiene un plan activo
    has_active_plan = False
    if profile:
        plan_result = await db.execute(
            select(GeneratedPlan)
            .where(GeneratedPlan.user_profile_id == profile.id)
            .where(GeneratedPlan.is_active == True)
            .limit(1)
        )
        has_active_plan = plan_result.scalars().first() is not None

    return {
        "onboarding_completed": current_user.onboarding_completed,
        "has_profile": profile is not None,
        "steps_completed": steps_completed,
        "next_step": next_step,
        "has_active_plan": has_active_plan
    }


# === Helper: Auto-populate plan tracking tables ===

async def _populate_plan_tracking(db: AsyncSession, plan: GeneratedPlan, plan_structure: dict):
    """
    Explota el plan_structure JSON en tablas normalizadas para tracking.
    Crea PlanWeek, PlanDay, PlanExercise para cada semana del plan.
    """
    weeks_data = plan_structure.get("weeks", [])
    phases_data = plan_structure.get("phases", [])
    total_weeks = plan_structure.get("total_weeks", plan.total_weeks)

    # Mapear phase por week_number
    week_to_phase = {}
    for phase in phases_data:
        phase_weeks = phase.get("weeks", [])
        for wn in phase_weeks:
            week_to_phase[wn] = phase.get("name", "")

    # Semanas representativas indexadas por week_number
    representative_weeks = {w.get("week_number"): w for w in weeks_data}

    for week_num in range(1, total_weeks + 1):
        phase_name = week_to_phase.get(week_num, "")

        # Buscar la semana representativa de esta fase
        week_data = representative_weeks.get(week_num)
        if not week_data:
            for rw in weeks_data:
                if rw.get("phase") == phase_name:
                    week_data = rw
                    break

        is_deload = week_data.get("is_deload", False) if week_data else False
        focus = week_data.get("focus", "") if week_data else ""
        progression_notes = week_data.get("progression_notes", "") if week_data else ""

        plan_week = PlanWeek(
            plan_id=plan.id,
            week_number=week_num,
            phase_name=phase_name,
            is_deload=is_deload,
            focus=focus,
            progression_notes=progression_notes,
            status="in_progress" if week_num == plan.current_week else "pending",
            started_at=datetime.now(timezone.utc) if week_num == plan.current_week else None,
        )
        db.add(plan_week)
        await db.flush()

        # Crear días
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
                status="pending",
            )
            db.add(plan_day)
            await db.flush()

            # Crear ejercicios
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
                    sort_order=idx,
                )
                db.add(plan_exercise)

    await db.commit()
