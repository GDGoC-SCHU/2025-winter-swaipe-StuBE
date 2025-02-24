from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from src.infrastructure.studentCard.persistence.database import get_db
from src.domain.studentCard.service.barcode_service import BarcodeService
from src.domain.studentCard.service.ocr_service import OCRService
from src.infrastructure.studentCard.external.barcode_reader import BarcodeReader
from src.infrastructure.studentCard.external.gpt_vision_reader import GPTVisionReader
from src.domain.studentCard.repository.repositories import SQLAlchemyStudentRepository
from src.domain.studentCard.exception.exceptions import (
    DomainException,
    InvalidImageException,
    BarcodeProcessingException,
)
from src.domain.studentCard.entity.student import Student
from datetime import datetime
import asyncio

router = APIRouter()


def get_ocr_reader():
    return GPTVisionReader()


def get_barcode_reader():
    return BarcodeReader()


def get_student_repository(db: Session = Depends(get_db)):
    return SQLAlchemyStudentRepository(db)


def get_ocr_service(
    reader: GPTVisionReader = Depends(get_ocr_reader),
    repository: SQLAlchemyStudentRepository = Depends(get_student_repository),
):
    return OCRService(reader, repository)


def get_barcode_service(reader: BarcodeReader = Depends(get_barcode_reader)):
    return BarcodeService(reader)


@router.post("/student-card/analyze")
async def analyze_student_card(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    ocr_service: OCRService = Depends(get_ocr_service),
    barcode_service: BarcodeService = Depends(get_barcode_service),
    student_repository: SQLAlchemyStudentRepository = Depends(get_student_repository),
):
    # 이미지 형식 검증
    if not image.content_type.startswith("image/"):
        raise InvalidImageException("Invalid file type. Please upload an image file.")

    try:
        contents = await image.read()

        # 병렬 처리로 변경
        barcode_task = asyncio.create_task(barcode_service.extract_barcode(contents))
        ocr_task = asyncio.create_task(ocr_service.extract_info(contents))

        # 동시 실행 후 결과 대기
        barcode_data, student_info = await asyncio.gather(barcode_task, ocr_task)

        if not barcode_data:
            raise BarcodeProcessingException(
                "Could not extract student number from barcode"
            )

        # 학생 정보 생성 또는 업데이트
        student = Student.create(
            student_number=barcode_data,
            department=student_info.department,
            year=student_info.year,
        )

        # DB에 저장
        await student_repository.save(student)

        return {
            "status": "success",
            "data": {
                "student_number": barcode_data,
                "department": student_info.department,
                "year": student_info.year,
                "name": student_info.name,
                "processed_at": datetime.utcnow().isoformat(),
            },
        }

    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while processing image: {str(e)}",
        )
