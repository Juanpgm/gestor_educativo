# Deployment

## Docker Compose (Local/Dev)

```bash
docker compose up -d     # Start all services
docker compose logs -f   # Follow logs
docker compose down      # Stop
```

Services:

- **app**: FastAPI on port 8000
- **db**: PostgreSQL 16 on port 5432
- **pgadmin**: PgAdmin4 on port 5050

## Railway (Production MVP)

### Setup

1. Create account at https://railway.app/
2. Create new project from GitHub repo
3. Add PostgreSQL plugin
4. Set environment variables (copy from `secrets/.env.example`)

### Configuration

The `railway.toml` configures:

- Dockerfile-based build
- Start command: `alembic upgrade head && uvicorn ...`
- Health check at `/health`
- Auto-restart on failure

### Environment Variables

Set these in Railway dashboard:

- `DATABASE_URL` — from Railway PostgreSQL plugin
- `SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- `ENCRYPTION_KEY` — generate with `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
- `OPENAI_API_KEY` — from OpenAI dashboard
- Other settings from `.env.example`

### Estimated Cost

- Railway Starter: ~$5/month (including PostgreSQL)
- OpenAI (gpt-4o-mini): ~$0.15/1M input tokens
- Total: **< $20/month** for MVP scale

## Cloud Migration

The app is cloud-portable:

- **GCP**: Cloud Run + Cloud SQL
- **AWS**: ECS/Fargate + RDS
- **Azure**: Container Apps + Azure Database for PostgreSQL

Just change `DATABASE_URL` and deploy the Docker image.
