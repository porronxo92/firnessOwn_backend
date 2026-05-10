from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Numeric, SmallInteger, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class PlanWeek(Base):
    """Semana del plan de entrenamiento (normalizada desde plan_structure JSON)"""
    __tablename__ = "plan_weeks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("generated_plans.id", ondelete="CASCADE"), nullable=False)

    week_number = Column(Integer, nullable=False)
    phase_name = Column(String(100), nullable=True)
    is_deload = Column(Boolean, default=False)
    focus = Column(Text, nullable=True)
    progression_notes = Column(Text, nullable=True)

    # Status: pending, in_progress, completed
    status = Column(String(20), default="pending", nullable=False)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    plan = relationship("GeneratedPlan", back_populates="plan_weeks")
    days = relationship("PlanDay", back_populates="week", cascade="all, delete-orphan", order_by="PlanDay.day_number")

    __table_args__ = (
        Index("idx_plan_weeks_plan_week", "plan_id", "week_number", unique=True),
    )


class PlanDay(Base):
    """Día dentro de una semana del plan"""
    __tablename__ = "plan_days"

    id = Column(Integer, primary_key=True, index=True)
    week_id = Column(Integer, ForeignKey("plan_weeks.id", ondelete="CASCADE"), nullable=False)

    day_number = Column(SmallInteger, nullable=False)  # 1-7
    day_name = Column(String(20), nullable=False)  # Lunes, Martes...
    type = Column(String(30), nullable=False)  # strength, cardio, rest, active_recovery, hybrid
    session_name = Column(String(200), nullable=True)
    duration_minutes = Column(SmallInteger, nullable=True)
    session_notes = Column(Text, nullable=True)

    # Cardio details (nullable, solo si type=cardio)
    cardio_type = Column(String(50), nullable=True)
    cardio_duration_min = Column(SmallInteger, nullable=True)
    cardio_intensity = Column(String(20), nullable=True)
    cardio_distance_km = Column(Numeric(6, 2), nullable=True)
    cardio_notes = Column(Text, nullable=True)

    # Status: pending, completed, skipped
    status = Column(String(20), default="pending", nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    week = relationship("PlanWeek", back_populates="days")
    exercises = relationship("PlanExercise", back_populates="day", cascade="all, delete-orphan", order_by="PlanExercise.sort_order")

    __table_args__ = (
        Index("idx_plan_days_week_day", "week_id", "day_number", unique=True),
    )


class PlanExercise(Base):
    """Ejercicio planificado dentro de un día"""
    __tablename__ = "plan_exercises"

    id = Column(Integer, primary_key=True, index=True)
    day_id = Column(Integer, ForeignKey("plan_days.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(200), nullable=False)
    muscle_group = Column(String(50), nullable=True)
    sets = Column(SmallInteger, nullable=False, default=3)
    reps = Column(String(30), nullable=False, default="10")  # "8-10" or "12"
    rir = Column(String(20), nullable=True)
    rest_seconds = Column(SmallInteger, nullable=True)
    tempo = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    alternatives = Column(Text, nullable=True)  # comma-separated
    sort_order = Column(SmallInteger, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    day = relationship("PlanDay", back_populates="exercises")
    logs = relationship("ExerciseLog", back_populates="plan_exercise", cascade="all, delete-orphan", order_by="ExerciseLog.created_at.desc()")

    __table_args__ = (
        Index("idx_plan_exercises_day", "day_id", "sort_order"),
        Index("idx_plan_exercises_name", "name"),
    )


class ExerciseLog(Base):
    """Registro real de una serie ejecutada por el usuario"""
    __tablename__ = "exercise_logs"

    id = Column(Integer, primary_key=True, index=True)
    plan_exercise_id = Column(Integer, ForeignKey("plan_exercises.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    set_number = Column(SmallInteger, nullable=False)  # 1, 2, 3, 4...
    weight_kg = Column(Numeric(6, 2), nullable=True)
    reps_done = Column(SmallInteger, nullable=True)
    rir_actual = Column(String(10), nullable=True)
    rpe = Column(Numeric(3, 1), nullable=True)
    completed = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    plan_exercise = relationship("PlanExercise", back_populates="logs")

    __table_args__ = (
        Index("idx_exercise_logs_exercise", "plan_exercise_id", "created_at"),
        Index("idx_exercise_logs_user", "user_id", "created_at"),
    )
