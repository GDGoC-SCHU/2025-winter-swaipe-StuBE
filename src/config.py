from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    RELOAD: bool = True
    WORKERS: int = 1
    DEBUG: bool = True

    # Application
    APP_NAME: str = "Student Card API"
    API_PREFIX: str = "/api/v1"

    # OpenAI 설정
    OPENAI_API_KEY: str
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0
    openai_max_tokens: int = 1000

    # Vector DB 설정
    vector_db_path: str = "./vector_db"
    vector_db_collection: str = "student_card_analysis"
    PERSIST_DIRECTORY: str = "./vector_db"

    # 성능 설정
    max_parallel_requests: int = 3
    request_timeout: int = 30
    cache_ttl: int = 3600

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # 추가 환경 변수 허용


settings = Settings()
