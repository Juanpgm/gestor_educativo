# Architecture

## Overview

Gestor Educativo uses a layered async architecture:

```
┌─────────────────────────────────────┐
│           FastAPI (main.py)          │
│   Middleware: CORS, Rate Limit,      │
│   Security Headers, Audit Log        │
├──────────┬──────────┬───────────────┤
│  Auth    │  CRUD    │  Documents    │
│  Router  │  Routers │  Router       │
├──────────┴──────────┴───────────────┤
│          Services Layer              │
│  auth_service, document_service,     │
│  certification_service, email_service│
├─────────────────────────────────────┤
│         Template Agent               │
│  OCR → LLM Mapper → Template Builder │
├─────────────────────────────────────┤
│    SQLAlchemy 2.0 Async ORM          │
│    (Models + Alembic Migrations)     │
├─────────────────────────────────────┤
│         PostgreSQL 16                │
└─────────────────────────────────────┘
```

## Request Flow

1. **Request** → Middleware chain (security headers, rate limit, audit log)
2. **Router** → Validates input via Pydantic schemas
3. **Dependencies** → JWT auth, role check, DB session
4. **Service** → Business logic, encryption/decryption
5. **ORM** → Async SQLAlchemy query
6. **Response** → Pydantic serialization → JSON

## Design Decisions

- **Async everywhere**: asyncpg + async SQLAlchemy for non-blocking DB operations
- **Fernet encryption at rest**: PII fields encrypted before storage, decrypted on read
- **Structured logging**: JSON logs in production for machine parsing, console in dev
- **Cost monitoring**: Every LLM API call logged with token count and estimated cost
- **Multi-stage Docker**: Slim build image, separate runtime with Tesseract/Poppler
- **No raw SQL**: SQLAlchemy ORM prevents SQL injection by design
