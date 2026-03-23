"""Alumnos CRUD endpoints."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.models.alumno import Alumno, alumno_tutores
from app.models.tutor import Tutor
from app.schemas.alumno import AlumnoCreate, AlumnoResponse, AlumnoUpdate
from app.utils.encryption import decrypt_value, encrypt_value

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])


def _to_response(a: Alumno) -> AlumnoResponse:
    antiguedad = (date.today() - a.fecha_ingreso).days if a.fecha_ingreso else None
    return AlumnoResponse(
        cod_alumno=a.cod_alumno,
        identificacion=decrypt_value(a.identificacion),
        nombre=a.nombre,
        apellidos=a.apellidos,
        grado=a.grado,
        fecha_nacimiento=a.fecha_nacimiento,
        fecha_ingreso=a.fecha_ingreso,
        fecha_egreso=a.fecha_egreso,
        email=decrypt_value(a.email),
        telefono=decrypt_value(a.telefono),
        direccion=decrypt_value(a.direccion),
        antiguedad_dias=antiguedad,
        tutores=a.tutores,
        created_at=a.created_at,
        updated_at=a.updated_at,
    )


@router.get("", response_model=list[AlumnoResponse])
async def list_alumnos(
    db: DB,
    user: CurrentUser,
    grado: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(Alumno).options(selectinload(Alumno.tutores))
    if grado:
        stmt = stmt.where(Alumno.grado == grado)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [_to_response(a) for a in result.scalars().all()]


@router.get("/{cod_alumno}", response_model=AlumnoResponse)
async def get_alumno(db: DB, user: CurrentUser, cod_alumno: str):
    result = await db.execute(
        select(Alumno).options(selectinload(Alumno.tutores)).where(Alumno.cod_alumno == cod_alumno)
    )
    alumno = result.scalar_one_or_none()
    if not alumno:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alumno not found")
    return _to_response(alumno)


@router.post("", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
async def create_alumno(db: DB, data: AlumnoCreate, user: AdminOrSecretaria):
    alumno = Alumno(
        cod_alumno=data.cod_alumno,
        identificacion=encrypt_value(data.identificacion),
        nombre=data.nombre,
        apellidos=data.apellidos,
        grado=data.grado,
        fecha_nacimiento=data.fecha_nacimiento,
        fecha_ingreso=data.fecha_ingreso,
        fecha_egreso=data.fecha_egreso,
        email=encrypt_value(data.email),
        telefono=encrypt_value(data.telefono),
        direccion=encrypt_value(data.direccion),
    )
    if data.tutor_ids:
        result = await db.execute(select(Tutor).where(Tutor.cod_tutor.in_(data.tutor_ids)))
        alumno.tutores = list(result.scalars().all())
    db.add(alumno)
    await db.flush()
    await db.refresh(alumno, ["tutores"])
    return _to_response(alumno)


@router.put("/{cod_alumno}", response_model=AlumnoResponse)
async def update_alumno(db: DB, cod_alumno: str, data: AlumnoUpdate, user: AdminOrSecretaria):
    result = await db.execute(
        select(Alumno).options(selectinload(Alumno.tutores)).where(Alumno.cod_alumno == cod_alumno)
    )
    alumno = result.scalar_one_or_none()
    if not alumno:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alumno not found")

    update_fields = data.model_dump(exclude_unset=True, exclude={"tutor_ids"})
    for field in ("email", "telefono", "direccion"):
        if field in update_fields and update_fields[field] is not None:
            update_fields[field] = encrypt_value(update_fields[field])
    for k, v in update_fields.items():
        setattr(alumno, k, v)

    if data.tutor_ids is not None:
        result = await db.execute(select(Tutor).where(Tutor.cod_tutor.in_(data.tutor_ids)))
        alumno.tutores = list(result.scalars().all())

    await db.flush()
    await db.refresh(alumno)
    await db.refresh(alumno, ["tutores"])
    return _to_response(alumno)


@router.delete("/{cod_alumno}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alumno(db: DB, cod_alumno: str, user: AdminOrSecretaria):
    result = await db.execute(select(Alumno).where(Alumno.cod_alumno == cod_alumno))
    alumno = result.scalar_one_or_none()
    if not alumno:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Alumno not found")
    await db.delete(alumno)
