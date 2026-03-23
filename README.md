# Gestor Educativo

Backend para gestión de expedientes educativos: notas, diplomas y certificados.
Inspirado en [Parchment](https://www.parchment.com/).

## Stack

| Component      | Technology                       |
| -------------- | -------------------------------- |
| Framework      | FastAPI (Python 3.11+)           |
| Database       | PostgreSQL 16 + asyncpg          |
| ORM            | SQLAlchemy 2.0 (async)           |
| Auth           | JWT (HS256) + bcrypt             |
| PII Encryption | Fernet (AES-128-CBC)             |
| Document Gen   | docxtpl + Tesseract OCR + OpenAI |
| Email          | Gmail API (OAuth2)               |
| Deployment     | Docker + Railway                 |

## Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd gestor_educativo

# 2. Copy env file
cp secrets/.env.example secrets/.env
# Edit secrets/.env with your values

# 3. Start with Docker Compose
docker compose up -d

# 4. Run migrations
docker compose exec app alembic upgrade head

# 5. Access
# API:     http://localhost:8000
# Docs:    http://localhost:8000/docs
# PgAdmin: http://localhost:5050
```

### Local Development (without Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
make dev
```

## Project Structure

```
app/
├── main.py             # FastAPI app entry point
├── config.py           # Settings (Pydantic BaseSettings)
├── database.py         # Async SQLAlchemy setup
├── core/               # Security, logging, middleware
├── models/             # 11 SQLAlchemy ORM models
├── schemas/            # 9 Pydantic schema files
├── api/v1/             # 9 API router files
├── services/           # Business logic (auth, cert, email, docs)
├── template_agent/     # OCR → LLM → template pipeline
└── utils/              # Encryption utilities
alembic/                # Database migrations
secrets/                # Environment variables (gitignored)
templates/              # .docx templates for document generation
docs/                   # Detailed documentation
```

## Documentation

| Document                                           | Description                               |
| -------------------------------------------------- | ----------------------------------------- |
| [Architecture](docs/architecture.md)               | System architecture and design decisions  |
| [Database Schema](docs/database-schema.md)         | All tables, relationships, and ER diagram |
| [API Reference](docs/api-reference.md)             | Complete endpoint documentation           |
| [Authentication](docs/authentication.md)           | JWT auth flow and role-based access       |
| [Document Generation](docs/document-generation.md) | Template filling and mass generation      |
| [Template Agent](docs/template-agent.md)           | OCR + LLM pipeline                        |
| [Certification](docs/certification-system.md)      | Document verification via hash + QR       |
| [Gmail Integration](docs/gmail-integration.md)     | Email setup and sending                   |
| [Deployment](docs/deployment.md)                   | Docker, Railway, and cloud deployment     |
| [Security](docs/security.md)                       | PII encryption, rate limiting, headers    |
| [Cost Monitoring](docs/cost-monitoring.md)         | LLM cost tracking                         |

## License

Private — All rights reserved.
