"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="secrets/.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────
    app_name: str = "Gestor Educativo"
    app_version: str = "0.1.0"
    debug: bool = False
    environment: str = "development"  # development | staging | production
    base_url: str = "http://localhost:8000"
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"

    # ── Database ─────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gestor_educativo"

    # ── Security ─────────────────────────────────────────
    secret_key: str = "CHANGE-ME-generate-a-random-256-bit-key"
    encryption_key: str = "CHANGE-ME-generate-a-fernet-key"  # Fernet key for PII
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Rate Limiting ────────────────────────────────────
    rate_limit_per_minute: int = 100
    rate_limit_login_per_minute: int = 5

    # ── LLM ──────────────────────────────────────────────
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    llm_max_tokens: int = 4096

    # ── Gmail API ────────────────────────────────────────
    gmail_credentials_path: str = "secrets/credentials/gmail_credentials.json"
    gmail_token_path: str = "secrets/credentials/gmail_token.json"
    gmail_sender_email: str = ""

    # ── File Paths ───────────────────────────────────────
    upload_dir: str = "uploads"
    generated_dir: str = "generated"
    templates_dir: str = "templates"

    @property
    def async_database_url(self) -> str:
        """Ensure the URL uses the asyncpg driver (Railway provides plain postgresql://)."""
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def sync_database_url(self) -> str:
        """For Alembic migrations (sync driver)."""
        url = self.async_database_url
        return url.replace("+asyncpg", "+psycopg2")

    @property
    def origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    def ensure_dirs(self) -> None:
        """Create runtime directories if they don't exist."""
        for d in (self.upload_dir, self.generated_dir, self.templates_dir):
            Path(d).mkdir(parents=True, exist_ok=True)
        Path(self.templates_dir, "diplomas").mkdir(parents=True, exist_ok=True)
        Path(self.templates_dir, "certificados").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
