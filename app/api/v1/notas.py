"""Notas CRUD endpoints and Periodos Academicos."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.models.nota import Nota
from app.models.periodo import PeriodoAcademico
from app.schemas.nota import (
    NotaBulkCreate,
    NotaCreate,
    NotaResponse,
    NotaUpdate,
    PeriodoCreate,
    PeriodoResponse,
    PeriodoUpdate,
)

router = APIRouter(tags=["Notas"])


# ── Notas ────────────────────────────────────────────────────

def _nota_to_response(n: Nota) -> NotaResponse:
    return NotaResponse(
        id=n.id,
        cod_alumno=n.cod_alumno,
        cod_materia=n.cod_materia,
        cod_periodo=n.cod_periodo,
        nota=float(n.nota),
        nombre_alumno=f"{n.alumno.nombre} {n.alumno.apellidos}" if n.alumno else None,
        nombre_materia=n.materia.nombre_materia if n.materia else None,
        nombre_periodo=n.periodo.nombre if n.periodo else None,
        created_at=n.created_at,
        updated_at=n.updated_at,
    )


@router.get("/notas", response_model=list[NotaResponse])
async def list_notas(
    db: DB,
    user: CurrentUser,
    cod_alumno: str | None = None,
    cod_materia: str | None = None,
    cod_periodo: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
):
    stmt = (
        select(Nota)
        .options(selectinload(Nota.alumno), selectinload(Nota.materia), selectinload(Nota.periodo))
    )
    if cod_alumno:
        stmt = stmt.where(Nota.cod_alumno == cod_alumno)
    if cod_materia:
        stmt = stmt.where(Nota.cod_materia == cod_materia)
    if cod_periodo:
        stmt = stmt.where(Nota.cod_periodo == cod_periodo)
    result = await db.execute(stmt.offset(skip).limit(limit))
    return [_nota_to_response(n) for n in result.scalars().all()]


@router.get("/notas/{nota_id}", response_model=NotaResponse)
async def get_nota(db: DB, user: CurrentUser, nota_id: int):
    result = await db.execute(
        select(Nota)
        .options(selectinload(Nota.alumno), selectinload(Nota.materia), selectinload(Nota.periodo))
        .where(Nota.id == nota_id)
    )
    nota = result.scalar_one_or_none()
    if not nota:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nota not found")
    return _nota_to_response(nota)


@router.post("/notas", response_model=NotaResponse, status_code=status.HTTP_201_CREATED)
async def create_nota(db: DB, data: NotaCreate, user: AdminOrSecretaria):
    nota = Nota(**data.model_dump())
    db.add(nota)
    await db.flush()
    await db.refresh(nota, ["alumno", "materia", "periodo"])
    return _nota_to_response(nota)


@router.post("/notas/bulk", response_model=list[NotaResponse], status_code=status.HTTP_201_CREATED)
async def create_notas_bulk(db: DB, data: NotaBulkCreate, user: AdminOrSecretaria):
    notas = []
    for item in data.notas:
        n = Nota(**item.model_dump())
        db.add(n)
        notas.append(n)
    await db.flush()
    results = []
    for n in notas:
        await db.refresh(n, ["alumno", "materia", "periodo"])
        results.append(_nota_to_response(n))
    return results


@router.put("/notas/{nota_id}", response_model=NotaResponse)
async def update_nota(db: DB, nota_id: int, data: NotaUpdate, user: AdminOrSecretaria):
    result = await db.execute(select(Nota).where(Nota.id == nota_id))
    nota = result.scalar_one_or_none()
    if not nota:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nota not found")
    nota.nota = data.nota
    await db.flush()
    await db.refresh(nota)
    await db.refresh(nota, ["alumno", "materia", "periodo"])
    return _nota_to_response(nota)


@router.delete("/notas/{nota_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nota(db: DB, nota_id: int, user: AdminOrSecretaria):
    result = await db.execute(select(Nota).where(Nota.id == nota_id))
    nota = result.scalar_one_or_none()
    if not nota:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nota not found")
    await db.delete(nota)


# ── Periodos Academicos ─────────────────────────────────────

@router.get("/periodos", response_model=list[PeriodoResponse])
async def list_periodos(
    db: DB,
    user: CurrentUser,
    activo: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(PeriodoAcademico)
    if activo is not None:
        stmt = stmt.where(PeriodoAcademico.activo == activo)
    result = await db.execute(stmt.offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/periodos", response_model=PeriodoResponse, status_code=status.HTTP_201_CREATED)
async def create_periodo(db: DB, data: PeriodoCreate, user: AdminOrSecretaria):
    periodo = PeriodoAcademico(**data.model_dump())
    db.add(periodo)
    await db.flush()
    await db.refresh(periodo)
    return periodo


@router.put("/periodos/{cod_periodo}", response_model=PeriodoResponse)
async def update_periodo(db: DB, cod_periodo: str, data: PeriodoUpdate, user: AdminOrSecretaria):
    result = await db.execute(
        select(PeriodoAcademico).where(PeriodoAcademico.cod_periodo == cod_periodo)
    )
    periodo = result.scalar_one_or_none()
    if not periodo:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Periodo not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(periodo, k, v)
    await db.flush()
    await db.refresh(periodo)
    return periodo
