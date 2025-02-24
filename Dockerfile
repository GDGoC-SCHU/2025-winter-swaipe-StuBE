FROM python:3.11-slim

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    libzbar0 \
    tesseract-ocr \
    tesseract-ocr-kor \
    postgresql-client \
    libpq-dev \
    gcc \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install poetry

WORKDIR /app

# 의존성 파일만 먼저 복사하여 캐시 활용
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi --no-root

# 소스코드 복사
COPY . .

EXPOSE 8001 