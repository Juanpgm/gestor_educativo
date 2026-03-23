"""Tutores CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.models.tutor import Tutor
from app.schemas.tutor import TutorCreate, TutorResponse, TutorUpdate
from app.utils.encryption import decrypt_value, encrypt_value

router = APIRouter(prefix="/tutores", tags=["Tutores"])


def _to_response(t: Tutor) -> TutorResponse:
    return TutorResponse(
        cod_tutor=t.cod_tutor,
        identificacion=decrypt_value(t.identificacion),
        nombre=t.nombre,
        apellidos=t.apellidos,
        parentesco=t.parentesco,
        fecha_nacimiento=t.fecha_nacimiento,
        email=decrypt_value(t.email),
        telefono=decrypt_value(t.telefono),
        direccion=decrypt_value(t.direccion),
        created_at=t.created_at,
        updated_at=t.updated_at,
    )


@router.get("", response_model=list[TutorResponse])
async def list_tutores(
    db: DB,
    user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(select(Tutor).offset(skip).limit(limit))
    return [_to_response(t) for t in result.scalars().all()]


@router.get("/{cod_tutor}", response_model=TutorResponse)
async def get_tutor(db: DB, user: CurrentUser, cod_tutor: str):
    result = await db.execute(select(Tutor).where(Tutor.cod_tutor == cod_tutor))
    tutor = result.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tutor not found")
    return _to_response(tutor)


@router.post("", response_model=TutorResponse, status_code=status.HTTP_201_CREATED)
async def create_tutor(db: DB, data: TutorCreate, user: AdminOrSecretaria):
    tutor = Tutor(
        cod_tutor=data.cod_tutor,
        identificacion=encrypt_value(data.identificacion),
        nombre=data.nombre,
        apellidos=data.apellidos,
        parentesco=data.parentesco,
        fecha_nacimiento=data.fecha_nacimiento,
        email=encrypt_value(data.email),
        telefono=encrypt_value(data.telefono),
        direccion=encrypt_value(data.direccion),
    )
    db.add(tutor)
    await db.flush()
    await db.refresh(tutor)
    return _to_response(tutor)


@router.put("/{cod_tutor}", response_model=TutorResponse)
async def update_tutor(db: DB, cod_tutor: str, data: TutorUpdate, user: AdminOrSecretaria):
    result = await db.execute(select(Tutor).where(Tutor.cod_tutor == cod_tutor))
    tutor = result.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tutor not found")

    update_fields = data.model_dump(exclude_unset=True)
    for field in ("email", "telefono", "direccion"):
        if field in update_fields and update_fields[field] is not None:
            update_fields[field] = encrypt_value(update_fields[field])
    for k, v in update_fields.items():
        setattr(tutor, k, v)

    await db.flush()
    await db.refresh(tutor)
    return _to_response(tutor)


@router.delete("/{cod_tutor}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tutor(db: DB, cod_tutor: str, user: AdminOrSecretaria):
    result = await db.execute(select(Tutor).where(Tutor.cod_tutor == cod_tutor))
    tutor = result.scalar_one_or_none()
    if not tutor:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tutor not found")
    await db.delete(tutor)
