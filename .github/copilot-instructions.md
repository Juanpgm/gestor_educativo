# Copilot Instructions — Gestor Educativo

## Language & Framework

- Python 3.11+ with type hints
- FastAPI async endpoints
- SQLAlchemy 2.0 async ORM (mapped_column style)
- Pydantic v2 for schemas

## Code Style

- Use `ruff` for linting and formatting (configured in pyproject.toml)
- Line length: 100 characters
- Imports organized: stdlib → third-party → local
- Use `from __future__ import annotations` only when needed
- Prefer `str | None` over `Optional[str]`

## Patterns

- All CRUD follows: router → service/direct query → schema validation
- PII encryption via `app.utils.encryption.encrypt_value()` / `decrypt_value()`
- JWT auth via `app.api.deps.CurrentUser` dependency
- Role checks via `app.api.deps.require_roles()`
- Structured logging: `logger = get_logger(__name__)`
- DB sessions: `db: DB` parameter (AsyncSession from deps.py)

## Testing

- pytest with pytest-asyncio
- Test database: separate PostgreSQL database or SQLite for unit tests
- Use `httpx.AsyncClient` with `app` for integration tests

## Security Rules

- Never log PII values, only encrypted forms
- Always validate file uploads (type, size)
- Rate limiting is enforced via middleware
- SQL injection prevented by SQLAlchemy ORM (never raw SQL)
- XSS prevented by JSON-only API responses
