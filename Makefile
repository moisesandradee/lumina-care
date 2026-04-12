# Makefile for Lumina Care Project

.PHONY: help setup test test-backend test-frontend test-coverage lint format clean

help:
	@echo "Lumina Care Development Commands"
	@echo "=================================="
	@echo "make setup           - Install dependencies"
	@echo "make test            - Run all tests"
	@echo "make test-backend    - Run FastAPI backend tests"
	@echo "make test-frontend   - Run Next.js frontend tests"
	@echo "make test-coverage   - Run tests with coverage report"
	@echo "make lint            - Run linting (ESLint + Ruff)"
	@echo "make format          - Format code (Prettier + Black)"
	@echo "make type-check      - Run type checking"
	@echo "make validate        - Full validation (type-check + lint + test)"
	@echo "make clean           - Clean build artifacts"

setup:
	npm install
	poetry install

dev-frontend:
	cd src/web && npm run dev

dev-backend:
	poetry run uvicorn src.api.main:app --reload --port 8000

test:
	@echo "Running all tests..."
	ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ -v
	npm run test -- --coverage

test-backend:
	@echo "Running backend tests..."
	ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ -v

test-backend-quick:
	@echo "Running backend tests (quick)..."
	ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/test_main.py -v

test-frontend:
	@echo "Running frontend tests..."
	npm run test -- --coverage

test-coverage:
	@echo "Running tests with coverage..."
	ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ --cov=src/api --cov-report=html --cov-report=term
	npm run test:coverage

lint:
	@echo "Running linters..."
	npm run lint
	poetry run ruff check src/

format:
	@echo "Formatting code..."
	npm run format
	poetry run black src/
	poetry run isort src/

type-check:
	@echo "Running type checking..."
	npm run type-check
	poetry run mypy src/

validate:
	@echo "Full validation..."
	npm run type-check
	npm run lint
	npm run format:check
	ANTHROPIC_API_KEY="sk-test-key" poetry run pytest src/api/tests/ --cov=src/api
	npm run test:coverage

clean:
	rm -rf dist/ build/ .pytest_cache/ htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	npm run clean 2>/dev/null || true

.DEFAULT_GOAL := help
