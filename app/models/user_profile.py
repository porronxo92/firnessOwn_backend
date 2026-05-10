from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class UserProfile(Base):
    """Perfil completo del usuario con información de onboarding"""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Datos físicos
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)  # 'male', 'female', 'other', 'prefer_not_say'
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    
    # Objetivos
    primary_goal = Column(String(50), nullable=True)  # 'hypertrophy', 'strength', 'weight_loss', 'endurance', 'marathon', 'half_marathon', 'bodyweight', 'general_fitness'
    secondary_goals = Column(JSON, nullable=True)  # Lista de objetivos secundarios
    target_weight_kg = Column(Float, nullable=True)
    
    # Disponibilidad
    training_days_per_week = Column(Integer, nullable=True)  # 1-7
    preferred_days = Column(JSON, nullable=True)  # ['monday', 'wednesday', 'friday']
    session_duration_minutes = Column(Integer, nullable=True)  # Duración preferida por sesión
    
    # Periodo de entrenamiento
    training_period = Column(String(20), nullable=True)  # 'short' (4-8 sem), 'medium' (12-16 sem), 'long' (20+ sem)
    start_date = Column(DateTime(timezone=True), nullable=True)
    target_event_date = Column(DateTime(timezone=True), nullable=True)  # Si prepara evento específico
    target_event_name = Column(String(200), nullable=True)  # "Maratón de Madrid", etc.
    
    # Recursos disponibles
    has_gym_access = Column(Boolean, default=False)
    has_home_equipment = Column(Boolean, default=False)
    home_equipment_list = Column(JSON, nullable=True)  # ['dumbbells', 'pull_up_bar', 'resistance_bands']
    has_bike = Column(Boolean, default=False)
    bike_type = Column(String(50), nullable=True)  # 'road', 'mtb', 'indoor', 'gravel'
    has_running_gear = Column(Boolean, default=True)
    outdoor_space_available = Column(Boolean, default=False)
    pool_access = Column(Boolean, default=False)
    
    # Experiencia y nivel
    fitness_level = Column(String(20), nullable=True)  # 'beginner', 'intermediate', 'advanced'
    years_training = Column(Float, nullable=True)
    previous_injuries = Column(Text, nullable=True)
    health_conditions = Column(Text, nullable=True)
    
    # Alimentación
    diet_type = Column(String(50), nullable=True)  # 'omnivore', 'vegetarian', 'vegan', 'keto', 'paleo', 'other'
    meals_per_day = Column(Integer, nullable=True)
    tracks_calories = Column(Boolean, default=False)
    daily_calorie_target = Column(Integer, nullable=True)
    protein_target_grams = Column(Integer, nullable=True)
    
    # Preferencias de entrenamiento
    preferred_training_types = Column(JSON, nullable=True)  # ['strength', 'cardio', 'hiit', 'yoga']
    disliked_exercises = Column(JSON, nullable=True)  # Ejercicios que no quiere hacer
    favorite_exercises = Column(JSON, nullable=True)  # Ejercicios favoritos
    
    # Metadata
    onboarding_completed = Column(Boolean, default=False)
    onboarding_completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    generated_plans = relationship("GeneratedPlan", back_populates="user_profile", cascade="all, delete-orphan")
