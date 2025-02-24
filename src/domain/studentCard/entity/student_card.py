from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from src.infrastructure.common.persistence.database import Base


class StudentCard(Base):
    __tablename__ = "student_cards"

    id = Column(Integer, primary_key=True, index=True)
    student_number = Column(String, unique=True, index=True)
    department = Column(String)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
