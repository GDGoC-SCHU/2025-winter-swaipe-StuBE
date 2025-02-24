from src.infrastructure.studentCard.external.gpt_vision_reader import (
    GPTVisionReaderInterface,
)
from src.domain.studentCard.dto.schemas import StudentCardInfo
from src.domain.studentCard.repository.repositories import StudentRepositoryInterface
import logging
from tenacity import retry, stop_after_attempt, wait_exponential


class OCRService:
    def __init__(
        self, reader: GPTVisionReaderInterface, repository: StudentRepositoryInterface
    ):
        self._reader = reader
        self._repository = repository
        self._logger = logging.getLogger(__name__)

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def extract_info(self, image_bytes: bytes) -> StudentCardInfo:
        self._logger.info("OCR 처리 시작")
        try:
            result = await self._reader.extract_info(image_bytes)
            # 기존 학생 정보 확인
            existing_student = await self._repository.find_by_student_number(
                result.student_number
            )
            if existing_student:
                self._logger.info(f"기존 학생 정보 발견: {existing_student}")
            self._logger.info(f"OCR 처리 완료: {result}")
            return result
        except Exception as e:
            self._logger.error(f"OCR 처리 실패: {str(e)}")
            raise
