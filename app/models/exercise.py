from sqlalchemy import Column, Integer, String, SmallInteger, Text, ForeignKey
from app.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    phase_id = Column(Integer, ForeignKey("phases.id"))
    session_type = Column(String(10), nullable=False)
    name = Column(String(100), nullable=False)
    muscle_group = Column(String(50))
    muscle_desc = Column(Text)
    default_sets = Column(SmallInteger)
    default_reps = Column(String(20))
    rir = Column(String(10))
    notes = Column(Text)
    sort_order = Column(SmallInteger, default=0)
