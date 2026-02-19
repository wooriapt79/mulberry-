# Mulberry Spirit Score System - Makefile
# CTO Koda

.PHONY: help install dev-install test lint format clean docker-up docker-down db-setup

help:
	@echo "Mulberry Spirit Score System"
	@echo ""
	@echo "사용 가능한 명령어:"
	@echo "  make install      - 의존성 설치"
	@echo "  make dev-install  - 개발 의존성 설치"
	@echo "  make test         - 테스트 실행"
	@echo "  make lint         - 코드 검사"
	@echo "  make format       - 코드 포맷팅"
	@echo "  make clean        - 임시 파일 삭제"
	@echo "  make docker-up    - Docker 시작"
	@echo "  make docker-down  - Docker 종료"
	@echo "  make db-setup     - 데이터베이스 설정"
	@echo ""

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install pytest pytest-cov pytest-asyncio black flake8 isort

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

lint:
	flake8 src/ tests/ --max-line-length=100
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} +
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name 'htmlcov' -exec rm -rf {} +
	find . -type f -name '.coverage' -delete

docker-up:
	docker-compose up -d
	@echo "✅ Docker containers started"
	@echo "API: http://localhost:8000/docs"

docker-down:
	docker-compose down
	@echo "✅ Docker containers stopped"

docker-logs:
	docker-compose logs -f

db-setup:
	./scripts/setup_db.sh

run:
	python src/api.py

.DEFAULT_GOAL := help
