.PHONY: dev test lint format migrate build up down clean

# ── Development ────────────────────────────────────────────────
dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# ── Database ───────────────────────────────────────────────────
migrate:
	alembic upgrade head

migration:
	alembic revision --autogenerate -m "$(msg)"

# ── Testing ────────────────────────────────────────────────────
test:
	pytest tests/ -v --tb=short

test-cov:
	pytest tests/ -v --cov=app --cov-report=term-missing

# ── Code Quality ───────────────────────────────────────────────
lint:
	ruff check app/ tests/

format:
	ruff format app/ tests/

audit:
	pip-audit

# ── Docker ─────────────────────────────────────────────────────
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f app

# ── Cleanup ────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache
