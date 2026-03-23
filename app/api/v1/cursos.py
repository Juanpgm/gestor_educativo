"""Cursos CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.models.curso import Curso
from app.schemas.curso import CursoCreate, CursoResponse, CursoUpdate

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.get("", response_model=list[CursoResponse])
async def list_cursos(
    db: DB,
    user: CurrentUser,
    grado: str | None = None,
    activo: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(Curso)
    if grado:
        stmt = stmt.where(Curso.grado == grado)
    if activo is not None:
        stmt = stmt.where(Curso.activo == activo)
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{cod_curso}", response_model=CursoResponse)
async def get_curso(db: DB, user: CurrentUser, cod_curso: str):
    result = await db.execute(select(Curso).where(Curso.cod_curso == cod_curso))
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso not found")
    return curso


@router.post("", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def create_curso(db: DB, data: CursoCreate, user: AdminOrSecretaria):
    curso = Curso(**data.model_dump())
    db.add(curso)
    await db.flush()
    await db.refresh(curso)
    return curso


@router.put("/{cod_curso}", response_model=CursoResponse)
async def update_curso(db: DB, cod_curso: str, data: CursoUpdate, user: AdminOrSecretaria):
    result = await db.execute(select(Curso).where(Curso.cod_curso == cod_curso))
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(curso, k, v)
    await db.flush()
    await db.refresh(curso)
    return curso


@router.delete("/{cod_curso}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(db: DB, cod_curso: str, user: AdminOrSecretaria):
    result = await db.execute(select(Curso).where(Curso.cod_curso == cod_curso))
    curso = result.scalar_one_or_none()
    if not curso:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Curso not found")
    await db.delete(curso)
