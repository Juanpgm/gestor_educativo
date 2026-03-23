"""Materias CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.models.materia import Materia, MateriaGradoView, materia_grados
from app.schemas.materia import MateriaCreate, MateriaResponse, MateriaUpdate

router = APIRouter(prefix="/materias", tags=["Materias"])


def _to_response(m: Materia) -> MateriaResponse:
    grados_list = [g.grado for g in m.grados] if m.grados else []
    return MateriaResponse(
        cod_materia=m.cod_materia,
        nombre_materia=m.nombre_materia,
        descripcion=m.descripcion,
        activo=m.activo,
        grados=grados_list,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


@router.get("", response_model=list[MateriaResponse])
async def list_materias(
    db: DB,
    user: CurrentUser,
    grado: str | None = None,
    activo: bool | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(Materia)
    if activo is not None:
        stmt = stmt.where(Materia.activo == activo)
    if grado:
        stmt = stmt.join(materia_grados).where(materia_grados.c.grado == grado)
    result = await db.execute(stmt.offset(skip).limit(limit))
    return [_to_response(m) for m in result.scalars().unique().all()]


@router.get("/{cod_materia}", response_model=MateriaResponse)
async def get_materia(db: DB, user: CurrentUser, cod_materia: str):
    result = await db.execute(select(Materia).where(Materia.cod_materia == cod_materia))
    materia = result.scalar_one_or_none()
    if not materia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Materia not found")
    return _to_response(materia)


@router.post("", response_model=MateriaResponse, status_code=status.HTTP_201_CREATED)
async def create_materia(db: DB, data: MateriaCreate, user: AdminOrSecretaria):
    materia = Materia(
        cod_materia=data.cod_materia,
        nombre_materia=data.nombre_materia,
        descripcion=data.descripcion,
        activo=data.activo,
    )
    db.add(materia)
    await db.flush()

    # Add grados
    for grado in data.grados:
        await db.execute(
            materia_grados.insert().values(cod_materia=data.cod_materia, grado=grado)
        )
    await db.refresh(materia, ["grados"])
    return _to_response(materia)


@router.put("/{cod_materia}", response_model=MateriaResponse)
async def update_materia(db: DB, cod_materia: str, data: MateriaUpdate, user: AdminOrSecretaria):
    result = await db.execute(select(Materia).where(Materia.cod_materia == cod_materia))
    materia = result.scalar_one_or_none()
    if not materia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Materia not found")

    for k, v in data.model_dump(exclude_unset=True, exclude={"grados"}).items():
        setattr(materia, k, v)

    if data.grados is not None:
        await db.execute(materia_grados.delete().where(materia_grados.c.cod_materia == cod_materia))
        for grado in data.grados:
            await db.execute(
                materia_grados.insert().values(cod_materia=cod_materia, grado=grado)
            )
    await db.flush()
    await db.refresh(materia)
    await db.refresh(materia, ["grados"])
    return _to_response(materia)


@router.delete("/{cod_materia}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_materia(db: DB, cod_materia: str, user: AdminOrSecretaria):
    result = await db.execute(select(Materia).where(Materia.cod_materia == cod_materia))
    materia = result.scalar_one_or_none()
    if not materia:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Materia not found")
    await db.delete(materia)
