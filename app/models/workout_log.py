from sqlalchemy import Column, Integer, String, SmallInteger, Text, ForeignKey, DateTime, Date, Numeric, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database import Base


class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    custom_exercise_id = Column(Integer, ForeignKey("custom_exercises.id"), nullable=True)
    log_date = Column(Date, nullable=False)
    weight_kg = Column(Numeric(6, 2))
    sets_done = Column(SmallInteger)
    reps_done = Column(String(20))
    rir_actual = Column(String(10))
    rpe = Column(Numeric(3, 1))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "(exercise_id IS NOT NULL AND custom_exercise_id IS NULL) OR "
            "(exercise_id IS NULL AND custom_exercise_id IS NOT NULL)",
            name="chk_exercise"
        ),
        Index("idx_workout_logs_user_date", "user_id", "log_date"),
        Index("idx_workout_logs_exercise", "exercise_id", "user_id"),
    )


class CardioLog(Base):
    __tablename__ = "cardio_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    log_date = Column(Date, nullable=False)
    type = Column(String(20), nullable=False)
    duration_min = Column(SmallInteger)
    distance_km = Column(Numeric(6, 2))
    zone = Column(String(10))
    elevation_m = Column(SmallInteger)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_cardio_logs_user_date", "user_id", "log_date"),
    )
