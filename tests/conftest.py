"""Shared test fixtures and configuration."""

import asyncio
import os
from collections.abc import AsyncGenerator

# Set test environment variables BEFORE any app imports
os.environ.setdefault("ENCRYPTION_KEY", "dGVzdGtleV9mb3JfdGVzdGluZ19vbmx5XzMyYj0=")  # valid Fernet
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-jwt-tokens-only")
os.environ.setdefault("ENVIRONMENT", "test")
# Keep a PostgreSQL-looking URL so app.database module loads without pool_size errors;
# tests override the session with a SQLite engine anyway.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")

# Generate a proper Fernet key for tests if the default isn't valid
from cryptography.fernet import Fernet

_test_fernet_key = Fernet.generate_key().decode()
os.environ["ENCRYPTION_KEY"] = _test_fernet_key

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import JSON, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.core.security import create_access_token, hash_password
from app.database import Base, get_db
from app.main import app
from app.models.usuario import UserRole, Usuario

# ── SQLite JSONB workaround ──────────────────────────────────
# Replace PostgreSQL JSONB with generic JSON so SQLite can handle it.
JSONB_to_JSON = {JSONB: JSON}
for table in Base.metadata.tables.values():
    for column in table.columns:
        col_type = type(column.type)
        if col_type in JSONB_to_JSON:
            column.type = JSONB_to_JSON[col_type]()

# Use SQLite for tests (file-based)
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    # Reset cached settings and Fernet so tests use the test encryption key
    from app.config import get_settings as _gs
    _gs.cache_clear()

    import app.utils.encryption as enc_mod
    enc_mod._fernet = None
    enc_mod.settings = _gs()

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> Usuario:
    user = Usuario(
        email="admin@test.com",
        password_hash=hash_password("AdminPass123!"),
        nombre="Admin",
        apellidos="Test",
        rol=UserRole.admin,
        activo=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_token(admin_user: Usuario) -> str:
    return create_access_token({"sub": str(admin_user.id), "rol": admin_user.rol.value})


@pytest_asyncio.fixture
async def auth_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest_asyncio.fixture
async def secretaria_user(db_session: AsyncSession) -> Usuario:
    user = Usuario(
        email="secretaria@test.com",
        password_hash=hash_password("SecretPass123!"),
        nombre="Secretaria",
        apellidos="Test",
        rol=UserRole.secretaria,
        activo=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def secretaria_token(secretaria_user: Usuario) -> str:
    return create_access_token({"sub": str(secretaria_user.id), "rol": secretaria_user.rol.value})


@pytest_asyncio.fixture
async def secretaria_headers(secretaria_token: str) -> dict:
    return {"Authorization": f"Bearer {secretaria_token}"}


@pytest_asyncio.fixture
async def docente_user(db_session: AsyncSession) -> Usuario:
    user = Usuario(
        email="docente@test.com",
        password_hash=hash_password("DocentePass1!"),
        nombre="Docente",
        apellidos="Test",
        rol=UserRole.docente,
        activo=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def docente_token(docente_user: Usuario) -> str:
    return create_access_token({"sub": str(docente_user.id), "rol": docente_user.rol.value})


@pytest_asyncio.fixture
async def docente_headers(docente_token: str) -> dict:
    return {"Authorization": f"Bearer {docente_token}"}
