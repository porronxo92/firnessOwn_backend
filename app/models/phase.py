from sqlalchemy import Column, Integer, String, SmallInteger, Text
from app.database import Base


class Phase(Base):
    __tablename__ = "phases"

    id = Column(Integer, primary_key=True, index=True)
    num = Column(SmallInteger, nullable=False)
    name = Column(String(50), nullable=False)
    weeks_start = Column(SmallInteger, nullable=False)
    weeks_end = Column(SmallInteger, nullable=False)
    focus = Column(Text)
    description = Column(Text)
    series_per_muscle = Column(String(20))
    rep_range = Column(String(20))
    rir_target = Column(String(10))
    rest_seconds_min = Column(SmallInteger)
    rest_seconds_max = Column(SmallInteger)
