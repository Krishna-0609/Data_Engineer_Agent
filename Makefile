# =============================================================================
# AI Data Engineer Agent — Makefile
# =============================================================================

.PHONY: help dev down build test lint migrate seed clean

COMPOSE_DEV = docker compose -f infrastructure/docker-compose.dev.yml
BACKEND_CMD = $(COMPOSE_DEV) exec backend

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Development
# ---------------------------------------------------------------------------

dev: ## Start all services in development mode
	$(COMPOSE_DEV) up --build -d

down: ## Stop all services
	$(COMPOSE_DEV) down

logs: ## Tail all service logs
	$(COMPOSE_DEV) logs -f

restart: ## Restart all services
	$(COMPOSE_DEV) restart

build: ## Build all Docker images
	$(COMPOSE_DEV) build

# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------

backend-shell: ## Open a shell in the backend container
	$(BACKEND_CMD) bash

migrate: ## Run database migrations
	$(BACKEND_CMD) alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MSG="add users table")
	$(BACKEND_CMD) alembic revision --autogenerate -m "$(MSG)"

migrate-rollback: ## Rollback last migration
	$(BACKEND_CMD) alembic downgrade -1

seed: ## Seed database with sample data
	$(BACKEND_CMD) python -m app.infrastructure.database.seed

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: ## Run all tests
	$(COMPOSE_DEV) exec backend pytest -v
	cd frontend && npm test

test-backend: ## Run backend tests only
	$(COMPOSE_DEV) exec backend pytest -v --tb=short

test-backend-cov: ## Run backend tests with coverage
	$(COMPOSE_DEV) exec backend pytest --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests only
	cd frontend && npm test

# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------

lint: ## Run all linters
	$(COMPOSE_DEV) exec backend ruff check src/ tests/
	$(COMPOSE_DEV) exec backend ruff format --check src/ tests/
	cd frontend && npm run lint

lint-fix: ## Auto-fix lint issues
	$(COMPOSE_DEV) exec backend ruff check --fix src/ tests/
	$(COMPOSE_DEV) exec backend ruff format src/ tests/
	cd frontend && npm run lint -- --fix

type-check: ## Run type checking
	$(COMPOSE_DEV) exec backend mypy src/
	cd frontend && npx tsc --noEmit

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove all containers, volumes, and build artifacts
	$(COMPOSE_DEV) down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
