# Gestor Educativo — Agent Instructions

## Project Overview

Backend system for managing educational institution records (grades, diplomas, certificates).
Inspired by Parchment. Built with FastAPI + PostgreSQL + Docker.

## Architecture

- **Framework**: FastAPI (async, Python 3.11+)
- **Database**: PostgreSQL 16 with asyncpg driver, SQLAlchemy 2.0 async ORM
- **Auth**: JWT (HS256) via python-jose, bcrypt password hashing
- **PII Protection**: Fernet encryption at rest for sensitive fields
- **Document Generation**: docxtpl for .docx templates
- **OCR**: Tesseract via pytesseract + pdf2image
- **LLM**: OpenAI API for template variable mapping
- **Email**: Gmail API (OAuth2)
- **Deployment**: Docker + Railway

## Key Conventions

- All API endpoints under `/api/v1/`
- Async everywhere — all DB operations use `await`
- Pydantic v2 schemas with strict validation
- Structured logging via structlog (JSON in production)
- Configuration via Pydantic BaseSettings loading from `secrets/.env`
- PII fields (identificacion, email, telefono, direccion) are Fernet-encrypted in DB
- Role-based access: admin, secretaria, docente
- All dates as ISO 8601 strings in API responses

## File Structure

```
app/
├── main.py           # FastAPI app entry point
├── config.py         # Pydantic BaseSettings
├── database.py       # Async SQLAlchemy engine/session
├── core/             # Security, logging, middleware
├── models/           # SQLAlchemy ORM models
├── schemas/          # Pydantic request/response schemas
├── api/v1/           # API route handlers
├── services/         # Business logic layer
├── template_agent/   # OCR → LLM → template pipeline
└── utils/            # Encryption, helpers
```

## Database Models

- Alumno, Docente, Tutor (M:N alumno↔tutor)
- Curso, Materia (M:N materia↔grados)
- Nota, PeriodoAcademico
- Usuario (auth), DocumentoGenerado, Plantilla
- AuditLog, CostLog

## When Making Changes

1. Follow existing patterns for new endpoints
2. Always encrypt PII before storing, decrypt when returning
3. Add cost logging for any LLM API calls
4. Use `get_logger(__name__)` for structured logging
5. Add Alembic migrations for schema changes: `alembic revision --autogenerate -m "description"`
