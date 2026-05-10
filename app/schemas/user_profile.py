from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional, List, Any
from enum import Enum


class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_say = "prefer_not_say"


class GoalEnum(str, Enum):
    hypertrophy = "hypertrophy"
    strength = "strength"
    weight_loss = "weight_loss"
    endurance = "endurance"
    marathon = "marathon"
    half_marathon = "half_marathon"
    bodyweight = "bodyweight"
    general_fitness = "general_fitness"


class TrainingPeriodEnum(str, Enum):
    short = "short"  # 4-8 semanas
    medium = "medium"  # 12-16 semanas
    long = "long"  # 20+ semanas


class FitnessLevelEnum(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class DietTypeEnum(str, Enum):
    omnivore = "omnivore"
    vegetarian = "vegetarian"
    vegan = "vegan"
    keto = "keto"
    paleo = "paleo"
    other = "other"


class BikeTypeEnum(str, Enum):
    road = "road"
    mtb = "mtb"
    indoor = "indoor"
    gravel = "gravel"


# === Schemas para Onboarding por pasos ===

class OnboardingStep1(BaseModel):
    """Paso 1: Datos físicos básicos"""
    age: Optional[int] = Field(None, ge=14, le=100, description="Edad en años")
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = Field(None, ge=100, le=250, description="Altura en cm")
    weight_kg: Optional[float] = Field(None, ge=30, le=300, description="Peso en kg")
    body_fat_percentage: Optional[float] = Field(None, ge=3, le=60, description="% grasa corporal")


class OnboardingStep2(BaseModel):
    """Paso 2: Objetivos"""
    primary_goal: GoalEnum
    secondary_goals: Optional[List[GoalEnum]] = []
    target_weight_kg: Optional[float] = Field(None, ge=30, le=200)


class OnboardingStep3(BaseModel):
    """Paso 3: Disponibilidad y periodo"""
    training_days_per_week: int = Field(..., ge=1, le=7)
    preferred_days: Optional[List[str]] = []  # ['monday', 'wednesday', 'friday']
    session_duration_minutes: Optional[int] = Field(60, ge=15, le=180)
    training_period: TrainingPeriodEnum
    target_event_date: Optional[date] = None
    target_event_name: Optional[str] = None


class OnboardingStep4(BaseModel):
    """Paso 4: Recursos disponibles"""
    has_gym_access: bool = False
    has_home_equipment: bool = False
    home_equipment_list: Optional[List[str]] = []
    has_bike: bool = False
    bike_type: Optional[BikeTypeEnum] = None
    has_running_gear: bool = True
    outdoor_space_available: bool = False
    pool_access: bool = False


class OnboardingStep5(BaseModel):
    """Paso 5: Experiencia y salud"""
    fitness_level: FitnessLevelEnum
    years_training: Optional[float] = Field(None, ge=0, le=50)
    previous_injuries: Optional[str] = None
    health_conditions: Optional[str] = None


class OnboardingStep6(BaseModel):
    """Paso 6: Alimentación y preferencias"""
    diet_type: Optional[DietTypeEnum] = DietTypeEnum.omnivore
    meals_per_day: Optional[int] = Field(None, ge=1, le=8)
    tracks_calories: bool = False
    daily_calorie_target: Optional[int] = Field(None, ge=1000, le=6000)
    protein_target_grams: Optional[int] = Field(None, ge=30, le=400)
    preferred_training_types: Optional[List[str]] = []
    disliked_exercises: Optional[List[str]] = []
    favorite_exercises: Optional[List[str]] = []


# === Schema completo para crear/actualizar perfil ===

class UserProfileCreate(BaseModel):
    """Schema completo para crear un perfil de usuario"""
    # Datos físicos
    age: Optional[int] = Field(None, ge=14, le=100)
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = Field(None, ge=100, le=250)
    weight_kg: Optional[float] = Field(None, ge=30, le=300)
    body_fat_percentage: Optional[float] = Field(None, ge=3, le=60)
    
    # Objetivos
    primary_goal: Optional[GoalEnum] = None
    secondary_goals: Optional[List[str]] = []
    target_weight_kg: Optional[float] = None
    
    # Disponibilidad
    training_days_per_week: Optional[int] = Field(None, ge=1, le=7)
    preferred_days: Optional[List[str]] = []
    session_duration_minutes: Optional[int] = Field(60, ge=15, le=180)
    
    # Periodo
    training_period: Optional[TrainingPeriodEnum] = None
    start_date: Optional[datetime] = None
    target_event_date: Optional[datetime] = None
    target_event_name: Optional[str] = None
    
    # Recursos
    has_gym_access: bool = False
    has_home_equipment: bool = False
    home_equipment_list: Optional[List[str]] = []
    has_bike: bool = False
    bike_type: Optional[BikeTypeEnum] = None
    has_running_gear: bool = True
    outdoor_space_available: bool = False
    pool_access: bool = False
    
    # Experiencia
    fitness_level: Optional[FitnessLevelEnum] = None
    years_training: Optional[float] = None
    previous_injuries: Optional[str] = None
    health_conditions: Optional[str] = None
    
    # Alimentación
    diet_type: Optional[DietTypeEnum] = None
    meals_per_day: Optional[int] = None
    tracks_calories: bool = False
    daily_calorie_target: Optional[int] = None
    protein_target_grams: Optional[int] = None
    
    # Preferencias
    preferred_training_types: Optional[List[str]] = []
    disliked_exercises: Optional[List[str]] = []
    favorite_exercises: Optional[List[str]] = []


class UserProfileUpdate(UserProfileCreate):
    """Schema para actualizar perfil (todos los campos opcionales)"""
    pass


class UserProfileResponse(BaseModel):
    """Schema de respuesta del perfil de usuario"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    
    # Datos físicos
    age: Optional[int] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    
    # Objetivos
    primary_goal: Optional[str] = None
    secondary_goals: Optional[List[str]] = None
    target_weight_kg: Optional[float] = None
    
    # Disponibilidad
    training_days_per_week: Optional[int] = None
    preferred_days: Optional[List[str]] = None
    session_duration_minutes: Optional[int] = None
    
    # Periodo
    training_period: Optional[str] = None
    start_date: Optional[datetime] = None
    target_event_date: Optional[datetime] = None
    target_event_name: Optional[str] = None
    
    # Recursos
    has_gym_access: bool = False
    has_home_equipment: bool = False
    home_equipment_list: Optional[List[str]] = None
    has_bike: bool = False
    bike_type: Optional[str] = None
    has_running_gear: bool = True
    outdoor_space_available: bool = False
    pool_access: bool = False
    
    # Experiencia
    fitness_level: Optional[str] = None
    years_training: Optional[float] = None
    previous_injuries: Optional[str] = None
    health_conditions: Optional[str] = None
    
    # Alimentación
    diet_type: Optional[str] = None
    meals_per_day: Optional[int] = None
    tracks_calories: bool = False
    daily_calorie_target: Optional[int] = None
    protein_target_grams: Optional[int] = None
    
    # Preferencias
    preferred_training_types: Optional[List[str]] = None
    disliked_exercises: Optional[List[str]] = None
    favorite_exercises: Optional[List[str]] = None
    
    # Estado
    onboarding_completed: bool = False
    onboarding_completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
