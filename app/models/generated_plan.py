from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class GeneratedPlan(Base):
    """Plan de entrenamiento generado por Gemini AI"""
    __tablename__ = "generated_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_profile_id = Column(Integer, ForeignKey("user_profiles.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata del plan
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    total_weeks = Column(Integer, nullable=False)
    current_week = Column(Integer, default=1)
    
    # Tipo y enfoque
    plan_type = Column(String(50), nullable=False)  # 'strength', 'running', 'cycling', 'hybrid', 'bodyweight'
    primary_focus = Column(String(100), nullable=True)  # 'hypertrophy', 'marathon_prep', etc.
    
    # Contenido del plan (estructura completa generada por Gemini)
    plan_structure = Column(JSON, nullable=False)
    """
    Estructura esperada de plan_structure:
    {
        "overview": "Descripción general del plan",
        "phases": [
            {
                "phase_number": 1,
                "name": "Adaptación",
                "weeks": [1, 2, 3, 4],
                "focus": "Base building",
                "description": "..."
            }
        ],
        "weeks": [
            {
                "week_number": 1,
                "phase": "Adaptación",
                "focus": "...",
                "days": [
                    {
                        "day_number": 1,
                        "day_name": "Lunes",
                        "type": "strength",  # 'strength', 'cardio', 'rest', 'active_recovery'
                        "session_name": "Push Day",
                        "duration_minutes": 60,
                        "exercises": [
                            {
                                "name": "Press de banca",
                                "muscle_group": "chest",
                                "sets": 4,
                                "reps": "8-10",
                                "rir": "2-3",
                                "rest_seconds": 120,
                                "notes": "Mantener escápulas retraídas",
                                "alternatives": ["Press con mancuernas", "Flexiones"]
                            }
                        ],
                        "cardio": {
                            "type": "running",
                            "duration_minutes": 30,
                            "intensity": "Z2",
                            "distance_km": 5,
                            "notes": "..."
                        },
                        "warmup": [...],
                        "cooldown": [...],
                        "notes": "..."
                    }
                ],
                "weekly_notes": "...",
                "weekly_goals": ["...", "..."]
            }
        ],
        "nutrition_guidelines": {
            "daily_calories": 2500,
            "protein_grams": 180,
            "carbs_grams": 300,
            "fat_grams": 80,
            "pre_workout": "...",
            "post_workout": "...",
            "hydration": "..."
        },
        "progression_rules": {
            "strength": "...",
            "cardio": "...",
            "deload_weeks": [4, 8, 12]
        }
    }
    """
    
    # Estado del plan
    is_active = Column(Boolean, default=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Información de generación
    gemini_prompt_used = Column(Text, nullable=True)
    gemini_model_version = Column(String(50), nullable=True)
    generation_tokens = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_profile = relationship("UserProfile", back_populates="generated_plans")
    weekly_progress = relationship("WeeklyProgress", back_populates="plan", cascade="all, delete-orphan")
    plan_weeks = relationship("PlanWeek", back_populates="plan", cascade="all, delete-orphan", order_by="PlanWeek.week_number")


class WeeklyProgress(Base):
    """Seguimiento del progreso semanal del plan"""
    __tablename__ = "weekly_progress"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("generated_plans.id", ondelete="CASCADE"), nullable=False)
    
    week_number = Column(Integer, nullable=False)
    
    # Sesiones completadas
    sessions_planned = Column(Integer, default=0)
    sessions_completed = Column(Integer, default=0)
    
    # Notas y feedback
    user_notes = Column(Text, nullable=True)
    energy_level = Column(Integer, nullable=True)  # 1-10
    soreness_level = Column(Integer, nullable=True)  # 1-10
    motivation_level = Column(Integer, nullable=True)  # 1-10
    
    # Ajustes sugeridos por Gemini basados en feedback
    ai_feedback = Column(Text, nullable=True)
    suggested_adjustments = Column(JSON, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    plan = relationship("GeneratedPlan", back_populates="weekly_progress")
