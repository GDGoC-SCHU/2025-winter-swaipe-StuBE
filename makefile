.DEFAULT_GOAL := help

# 기본값 설정
PORT ?= 8001
HOST ?= 0.0.0.0

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  install              - Install dependencies"
	@echo "  docker-build        - Build Docker image"
	@echo "  docker-up           - Start services with Docker Compose"
	@echo "  docker-down         - Stop Docker Compose services"
	@echo "  docker-logs         - View Docker logs"
	@echo "  dev                 - Run development server with hot-reload (default port: 8001)"
	@echo "  test                - Run tests"
	@echo "  clean               - Clean temporary files"

install:
	poetry install

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

dev:
	docker-compose -f docker-compose.dev.yml up

test:
	PYTHONPATH=${PWD} poetry run pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	docker-compose down -v
	docker system prune -f