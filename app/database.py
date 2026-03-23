"""Async SQLAlchemy engine, session factory, and declarative Base."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# Railway free tier limits connections; use conservative pool sizing
_pool_size = 5 if settings.environment == "production" else 20
_max_overflow = 5 if settings.environment == "production" else 10

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_size=_pool_size,
    max_overflow=_max_overflow,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
