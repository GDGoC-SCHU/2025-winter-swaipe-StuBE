from src.infrastructure.common.persistence.database import Base, get_db, engine
from src.domain.studentCard.entity.student_card import StudentCard
import logging
from src.config import settings

# 로거 설정
logger = logging.getLogger(__name__)


async def init_student_card_db():
    """학생증 관련 데이터베이스 테이블 초기화"""
    try:
        async with engine.begin() as conn:
            # 기존 테이블 삭제 (개발 환경에서만)
            if settings.DEBUG:
                await conn.run_sync(Base.metadata.drop_all)

            # 테이블 생성
            await conn.run_sync(Base.metadata.create_all)
            logger.info("학생증 데이터베이스 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"학생증 데이터베이스 초기화 중 오류 발생: {str(e)}")
        raise

# get_db는 common에서 가져와서 사용
