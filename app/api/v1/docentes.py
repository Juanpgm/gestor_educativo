"""Docentes CRUD endpoints."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.models.docente import Docente
from app.models.materia import Materia
from app.schemas.docente import DocenteCreate, DocenteResponse, DocenteUpdate
from app.utils.encryption import decrypt_value, encrypt_value

router = APIRouter(prefix="/docentes", tags=["Docentes"])


def _to_response(d: Docente) -> DocenteResponse:
    antiguedad = (date.today() - d.fecha_ingreso).days if d.fecha_ingreso else None
    return DocenteResponse(
        cod_docente=d.cod_docente,
        identificacion=decrypt_value(d.identificacion),
        nombre=d.nombre,
        apellidos=d.apellidos,
        fecha_nacimiento=d.fecha_nacimiento,
        fecha_ingreso=d.fecha_ingreso,
        fecha_egreso=d.fecha_egreso,
        email=decrypt_value(d.email),
        telefono=decrypt_value(d.telefono),
        direccion=decrypt_value(d.direccion),
        antiguedad_dias=antiguedad,
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


@router.get("", response_model=list[DocenteResponse])
async def list_docentes(
    db: DB,
    user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(select(Docente).offset(skip).limit(limit))
    return [_to_response(d) for d in result.scalars().all()]


@router.get("/{cod_docente}", response_model=DocenteResponse)
async def get_docente(db: DB, user: CurrentUser, cod_docente: str):
    result = await db.execute(select(Docente).where(Docente.cod_docente == cod_docente))
    docente = result.scalar_one_or_none()
    if not docente:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Docente not found")
    return _to_response(docente)


@router.post("", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
async def create_docente(db: DB, data: DocenteCreate, user: AdminOrSecretaria):
    docente = Docente(
        cod_docente=data.cod_docente,
        identificacion=encrypt_value(data.identificacion),
        nombre=data.nombre,
        apellidos=data.apellidos,
        fecha_nacimiento=data.fecha_nacimiento,
        fecha_ingreso=data.fecha_ingreso,
        fecha_egreso=data.fecha_egreso,
        email=encrypt_value(data.email),
        telefono=encrypt_value(data.telefono),
        direccion=encrypt_value(data.direccion),
    )
    if data.materia_ids:
        result = await db.execute(select(Materia).where(Materia.cod_materia.in_(data.materia_ids)))
        docente.materias = list(result.scalars().all())
    db.add(docente)
    await db.flush()
    await db.refresh(docente)
    return _to_response(docente)


@router.put("/{cod_docente}", response_model=DocenteResponse)
async def update_docente(db: DB, cod_docente: str, data: DocenteUpdate, user: AdminOrSecretaria):
    result = await db.execute(select(Docente).where(Docente.cod_docente == cod_docente))
    docente = result.scalar_one_or_none()
    if not docente:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Docente not found")

    update_fields = data.model_dump(exclude_unset=True, exclude={"materia_ids"})
    for field in ("email", "telefono", "direccion"):
        if field in update_fields and update_fields[field] is not None:
            update_fields[field] = encrypt_value(update_fields[field])
    for k, v in update_fields.items():
        setattr(docente, k, v)

    if data.materia_ids is not None:
        result = await db.execute(select(Materia).where(Materia.cod_materia.in_(data.materia_ids)))
        docente.materias = list(result.scalars().all())

    await db.flush()
    await db.refresh(docente)
    return _to_response(docente)


@router.delete("/{cod_docente}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_docente(db: DB, cod_docente: str, user: AdminOrSecretaria):
    result = await db.execute(select(Docente).where(Docente.cod_docente == cod_docente))
    docente = result.scalar_one_or_none()
    if not docente:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Docente not found")
    await db.delete(docente)
