from sqlalchemy import Column, Integer, String, SmallInteger, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class CustomExercise(Base):
    __tablename__ = "custom_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    phase_id = Column(Integer, ForeignKey("phases.id"))
    session_type = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    muscle_group = Column(String(50))
    default_sets = Column(SmallInteger)
    default_reps = Column(String(20))
    rir = Column(String(10))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
