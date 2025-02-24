from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Student:
    student_number: str
    department: str
    year: int
    id: Optional[int] = None
    created_at: datetime = None
    updated_at: datetime = None

    @classmethod
    def create(cls, student_number: str, department: str, year: int):
        now = datetime.utcnow()
        return cls(
            student_number=student_number,
            department=department,
            year=year,
            created_at=now,
            updated_at=now
        )