.PHONY: help build up down restart logs backend-logs frontend-logs db-migrate db-upgrade clean

help:
	@echo "Archify - Code Analysis Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build all containers"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make restart        - Restart all services"
	@echo "  make logs           - View logs from all services"
	@echo "  make backend-logs   - View backend logs"
	@echo "  make frontend-logs  - View frontend logs"
	@echo "  make db-migrate     - Create new database migration"
	@echo "  make db-upgrade     - Apply database migrations"
	@echo "  make clean          - Remove all containers and volumes"
	@echo "  make shell-backend  - Open shell in backend container"
	@echo "  make shell-frontend - Open shell in frontend container"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo ""
	@echo "Services are starting..."
	@echo "Backend API: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

backend-logs:
	docker-compose logs -f backend

frontend-logs:
	docker-compose logs -f frontend

db-migrate:
	docker-compose exec backend alembic revision --autogenerate -m "$(message)"

db-upgrade:
	docker-compose exec backend alembic upgrade head

clean:
	docker-compose down -v
	docker system prune -f

shell-backend:
	docker-compose exec backend /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

install-backend:
	cd backend && pip install -r requirements.txt

install-frontend:
	cd frontend && npm install
