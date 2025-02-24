from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.studentCard.entity.student import Student
from src.domain.studentCard.entity.student_card import StudentCard
import logging

logger = logging.getLogger(__name__)


class StudentRepositoryInterface(ABC):
    @abstractmethod
    async def save(self, student: Student) -> Student:
        pass

    @abstractmethod
    async def find_by_student_number(self, student_number: str) -> Optional[Student]:
        pass


class SQLAlchemyStudentRepository(StudentRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, student: Student) -> Student:
        try:
            # StudentCard 객체 생성
            student_card = StudentCard(
                student_number=student.student_number,
                department=student.department,
                year=student.year,
            )
            self._session.add(student_card)
            await self._session.commit()
            await self._session.refresh(student_card)

            # Student 객체로 변환하여 반환
            return Student(
                id=student_card.id,
                student_number=student_card.student_number,
                department=student_card.department,
                year=student_card.year,
                created_at=student_card.created_at,
                updated_at=student_card.updated_at,
            )
        except Exception as e:
            await self._session.rollback()
            logger.error(f"학생 저장 중 오류 발생: {str(e)}")
            raise

    async def find_by_student_number(self, student_number: str) -> Optional[Student]:
        try:
            query = select(StudentCard).where(
                StudentCard.student_number == student_number
            )
            result = await self._session.execute(query)
            student_card = result.scalar_one_or_none()

            if student_card:
                return Student(
                    student_number=student_card.student_number,
                    department=student_card.department,
                    year=student_card.year,
                    id=student_card.id,
                    created_at=student_card.created_at,
                    updated_at=student_card.updated_at,
                )
            return None
        except Exception as e:
            logger.error(f"학생 조회 중 오류 발생: {str(e)}")
            return None
