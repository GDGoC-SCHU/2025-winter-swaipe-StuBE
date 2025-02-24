from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config import settings
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# SQLAlchemy 모델의 기본 클래스 생성
Base = declarative_base()

# 데이터베이스 URL 설정
DATABASE_URL = settings.DATABASE_URL

# 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG, future=True)

# 세션 팩토리 생성
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    """데이터베이스 세션 제공"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
