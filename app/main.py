"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import alumnos, auth, cursos, docentes, documentos, email, materias, notas, tutores
from app.config import get_settings
from app.core.logging import setup_logging
from app.core.middleware import setup_middleware
from app.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    setup_logging()
    settings.ensure_dirs()
    yield
    # Shutdown
    await engine.dispose()


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend para gestión de expedientes educativos: notas, diplomas y certificados.",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Middleware
setup_middleware(app)

# API v1 routers
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(alumnos.router, prefix=PREFIX)
app.include_router(docentes.router, prefix=PREFIX)
app.include_router(tutores.router, prefix=PREFIX)
app.include_router(cursos.router, prefix=PREFIX)
app.include_router(materias.router, prefix=PREFIX)
app.include_router(notas.router, prefix=PREFIX)
app.include_router(documentos.router, prefix=PREFIX)
app.include_router(email.router, prefix=PREFIX)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": settings.app_version}
