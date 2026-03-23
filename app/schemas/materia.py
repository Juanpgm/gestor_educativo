"""Materia schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class MateriaBase(BaseModel):
    cod_materia: str = Field(..., max_length=20)
    nombre_materia: str = Field(..., max_length=150)
    descripcion: str = Field(default="")
    activo: bool = True


class MateriaCreate(MateriaBase):
    grados: list[str] = Field(default_factory=list, description="List of grado codes")


class MateriaUpdate(BaseModel):
    nombre_materia: str | None = Field(None, max_length=150)
    descripcion: str | None = None
    activo: bool | None = None
    grados: list[str] | None = None


class MateriaResponse(BaseModel):
    cod_materia: str
    nombre_materia: str
    descripcion: str
    activo: bool
    grados: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
