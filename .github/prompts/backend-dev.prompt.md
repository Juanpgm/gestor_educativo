---
description: Backend development guidelines for Gestor Educativo
---

# Backend Development Prompt

When working on this backend:

1. **New endpoint**: Add router in `app/api/v1/`, import in `app/main.py`, follow CRUD pattern from existing routers.
2. **New model**: Create in `app/models/`, import in `app/models/__init__.py`, run `alembic revision --autogenerate`.
3. **New schema**: Create in `app/schemas/`, use Pydantic v2 `model_config = ConfigDict(from_attributes=True)`.
4. **PII fields**: Always encrypt with `encrypt_value()` before DB insert, decrypt with `decrypt_value()` on read.
5. **Auth**: Use `CurrentUser` for any authenticated endpoint, `AdminOrSecretaria` for write operations.
6. **LLM calls**: Log cost via `CostLog` model, use `settings.llm_model` for model name.
