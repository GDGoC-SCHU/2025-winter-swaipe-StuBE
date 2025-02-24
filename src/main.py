import uvicorn
from fastapi import FastAPI
from src.interfaces.api.routes import router
from src.config import settings
from src.infrastructure.studentCard.persistence.database import init_student_card_db
import logging

# 로거 설정
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

    @app.on_event("startup")
    async def startup_event():
        """애플리케이션 시작 시 실행되는 이벤트 핸들러"""
        try:
            logger.info("데이터베이스 초기화 시작")
            await init_student_card_db()
            logger.info("데이터베이스 초기화 완료")
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {str(e)}")
            raise

    # 라우터 등록
    app.include_router(router, prefix=settings.API_PREFIX)

    return app


app = create_app()

# 직접 실행 시 환경 변수 우선 적용
if __name__ == "__main__":
    import os

    port = int(os.getenv("PORT", settings.PORT))
    host = os.getenv("HOST", settings.HOST)

    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=settings.RELOAD,
        workers=settings.WORKERS,
    )
