---
description: Database and migration guidelines
---

# Database Prompt

## Schema conventions

- Primary keys: `cod_*` (VARCHAR) for domain entities, `id` (INTEGER autoincrement) for system tables
- Timestamps: `created_at` and `updated_at` with `server_default=func.now()`
- PII columns: marked with `comment="Encrypted PII"`
- JSONB: used for flexible metadata (documentos_generados.metadata_doc, plantillas.variables_mapeadas)

## Relationships

- M:N via association tables (alumno_tutores, docente_materias, materia_grados)
- FK naming: `fk_<table>_<column>`
- Index naming: `ix_<table>_<column>`

## Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "add_new_table"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```
