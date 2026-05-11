from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# === Schemas para Plan Generado ===

class GeneratedPlanCreate(BaseModel):
    """Schema para crear un plan generado"""
    name: str
    description: Optional[str] = None
    total_weeks: int = Field(..., ge=1, le=52)
    plan_type: str  # 'strength', 'running', 'cycling', 'hybrid', 'bodyweight'
    primary_focus: Optional[str] = None
    plan_structure: Dict[str, Any]
    gemini_prompt_used: Optional[str] = None
    gemini_model_version: Optional[str] = None


class PlanGenerationAccepted(BaseModel):
    """Respuesta inmediata cuando se lanza la generación en background"""
    plan_id: int
    status: str  # 'generating'
    message: str


class PlanGenerationStatus(BaseModel):
    """Estado actual de la generación de un plan"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    generation_status: str  # 'pending' | 'generating' | 'completed' | 'error'
    generation_error: Optional[str] = None
    name: str
    is_active: bool
    created_at: Optional[datetime] = None


class GeneratedPlanResponse(BaseModel):
    """Schema de respuesta del plan generado"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_profile_id: int
    name: str
    description: Optional[str] = None
    total_weeks: int
    current_week: int
    plan_type: str
    primary_focus: Optional[str] = None
    plan_structure: Dict[str, Any]
    is_active: bool
    generation_status: str = 'completed'
    generation_error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GeneratedPlanSummary(BaseModel):
    """Resumen del plan sin la estructura completa"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str] = None
    total_weeks: int
    current_week: int
    plan_type: str
    primary_focus: Optional[str] = None
    is_active: bool
    started_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class WeeklyProgressCreate(BaseModel):
    """Schema para crear progreso semanal"""
    plan_id: int
    week_number: int = Field(..., ge=1, le=52)
    sessions_planned: int = Field(0, ge=0)
    sessions_completed: int = Field(0, ge=0)
    user_notes: Optional[str] = None
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    soreness_level: Optional[int] = Field(None, ge=1, le=10)
    motivation_level: Optional[int] = Field(None, ge=1, le=10)


class WeeklyProgressUpdate(BaseModel):
    """Schema para actualizar progreso semanal"""
    sessions_completed: Optional[int] = Field(None, ge=0)
    user_notes: Optional[str] = None
    energy_level: Optional[int] = Field(None, ge=1, le=10)
    soreness_level: Optional[int] = Field(None, ge=1, le=10)
    motivation_level: Optional[int] = Field(None, ge=1, le=10)


class WeeklyProgressResponse(BaseModel):
    """Schema de respuesta del progreso semanal"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    plan_id: int
    week_number: int
    sessions_planned: int
    sessions_completed: int
    user_notes: Optional[str] = None
    energy_level: Optional[int] = None
    soreness_level: Optional[int] = None
    motivation_level: Optional[int] = None
    ai_feedback: Optional[str] = None
    suggested_adjustments: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


# === Schemas específicos para estructura del plan ===

class ExerciseDetail(BaseModel):
    """Detalle de un ejercicio en el plan"""
    name: str
    muscle_group: Optional[str] = None
    sets: int
    reps: str
    rir: Optional[str] = None
    rest_seconds: Optional[int] = None
    tempo: Optional[str] = None
    notes: Optional[str] = None
    alternatives: Optional[List[str]] = []


class CardioDetail(BaseModel):
    """Detalle de sesión de cardio"""
    type: str  # 'running', 'cycling', 'swimming', etc.
    duration_minutes: int
    intensity: Optional[str] = None  # 'Z1', 'Z2', etc.
    distance_km: Optional[float] = None
    notes: Optional[str] = None


class WarmupCooldown(BaseModel):
    """Ejercicio de calentamiento o vuelta a la calma"""
    name: str
    duration: str
    notes: Optional[str] = None


class DayPlan(BaseModel):
    """Plan de un día específico"""
    day_number: int
    day_name: str
    type: str  # 'strength', 'cardio', 'rest', 'active_recovery'
    session_name: str
    duration_minutes: Optional[int] = None
    warmup: Optional[List[WarmupCooldown]] = []
    exercises: Optional[List[ExerciseDetail]] = []
    cardio: Optional[CardioDetail] = None
    cooldown: Optional[List[WarmupCooldown]] = []
    session_notes: Optional[str] = None
    notes: Optional[str] = None


class WeekPlan(BaseModel):
    """Plan de una semana"""
    week_number: int
    phase: str
    is_deload: bool = False
    focus: Optional[str] = None
    progression_notes: Optional[str] = None
    days: List[DayPlan]
    weekly_volume: Optional[Dict[str, Any]] = None
    weekly_goals: Optional[List[str]] = []
    weekly_notes: Optional[str] = None


class PhasePlan(BaseModel):
    """Fase del plan"""
    phase_number: int
    name: str
    weeks: List[int]
    focus: str
    description: Optional[str] = None
    volume_adjustment: Optional[str] = None
    intensity_adjustment: Optional[str] = None


class NutritionGuidelines(BaseModel):
    """Guías de nutrición"""
    daily_calories: Optional[int] = None
    protein_grams: Optional[int] = None
    carbs_grams: Optional[int] = None
    fat_grams: Optional[int] = None
    pre_workout_meal: Optional[str] = None
    post_workout_meal: Optional[str] = None
    hydration_liters: Optional[float] = None
    supplements_suggested: Optional[List[str]] = []


class ProgressionRules(BaseModel):
    """Reglas de progresión"""
    strength: Optional[str] = None
    cardio: Optional[str] = None
    deload_protocol: Optional[str] = None


class FullPlanStructure(BaseModel):
    """Estructura completa del plan generado"""
    plan_name: str
    overview: str
    total_weeks: int
    phases: List[PhasePlan]
    weeks: List[WeekPlan]
    nutrition_guidelines: Optional[NutritionGuidelines] = None
    progression_rules: Optional[ProgressionRules] = None
    important_notes: Optional[List[str]] = []


# === Schemas para peticiones de Gemini ===

class GeneratePlanRequest(BaseModel):
    """Petición para generar un nuevo plan"""
    regenerate: bool = False  # Si es True, regenera el plan aunque ya exista uno


class AdjustmentFeedback(BaseModel):
    """Feedback para solicitar ajustes del plan"""
    week_number: int
    sessions_completed: int
    sessions_planned: int
    energy_level: int = Field(..., ge=1, le=10)
    soreness_level: int = Field(..., ge=1, le=10)
    motivation_level: int = Field(..., ge=1, le=10)
    user_notes: Optional[str] = None


class AdjustmentSuggestionResponse(BaseModel):
    """Respuesta con sugerencias de ajuste"""
    analysis: str
    adjustments: List[Dict[str, str]]
    motivation_message: str
    warnings: Optional[List[str]] = []
    next_week_focus: str


# === Schema para respuesta de la semana actual ===

class CurrentWeekResponse(BaseModel):
    """Respuesta con los datos de la semana actual"""
    plan_id: int
    plan_name: str
    week_number: int
    total_weeks: int
    phase_name: str
    is_deload: bool
    week_plan: WeekPlan
    progress: Optional[WeeklyProgressResponse] = None
