.PHONY: up down kill test lint fmt venv-init venv-activate venv-deactivate up-local up-db-redis

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make up          - Start the application and all services in Docker"
	@echo "  make down        - Stop all services and remove containers"
	@echo "  make kill        - Stop all services without removing containers"
	@echo "  make test        - Run tests (requires db service running)"
	@echo "  make lint        - Run linting (ruff + mypy)"
	@echo "  make fmt         - Format and fix code using ruff"

# Docker commands
up:
	@echo "Starting application and services in Docker..."
	docker-compose up 

up-d:
	@echo "Starting application and services in detached mode..."
	docker-compose up -d

up-db-redis:
	docker-compose up -d db redis

kill:
	@echo "Stopping all services without removing containers..."
	docker-compose kill

down:
	@echo "Stopping all services and removing containers..."
	docker-compose down

# Testing and linting
test: 
	make check-db
	@echo "Running tests..."
	docker-compose run --rm -e PYTHONPATH=/app api pytest tests/ -s -vv

lint:
	@echo "Running linting..."
	make fmt
	PYTHONPATH=. .venv/bin/mypy src/ tests/

fmt:
	@echo "Formatting and fixing code..."
	PYTHONPATH=. .venv/bin/ruff format src/ tests/
	PYTHONPATH=. .venv/bin/ruff check --no-cache --fix

# Helper targets
check-db:
	@echo "Checking if database service is running..."
	@docker-compose ps db | grep -q "Up" || (echo "Database service is not running. Starting it..." && docker-compose up -d db)
	@sleep 2  # Give the database a moment to be ready


migrations-create:
	@echo "Creating new migration..."
	docker-compose exec api alembic revision --autogenerate -m "$(message)"

migrations-up:
	@echo "Running migrations up..."
	docker-compose exec api alembic upgrade head

migrations-down:
	@echo "Running migrations down..."
	docker-compose exec api alembic downgrade -1

migrations-history:
	@echo "Showing migration history..."
	docker-compose exec api alembic history --verbose

generate_shipments:
	@echo "Generating shipments in the API container..."
	docker-compose exec api python create_shipments.py
