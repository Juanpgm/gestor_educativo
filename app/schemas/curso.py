"""Curso schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CursoBase(BaseModel):
    cod_curso: str = Field(..., max_length=20)
    nombre_curso: str = Field(..., max_length=150)
    descripcion: str = Field(default="")
    grado: str = Field(..., max_length=20)
    activo: bool = True


class CursoCreate(CursoBase):
    pass


class CursoUpdate(BaseModel):
    nombre_curso: str | None = Field(None, max_length=150)
    descripcion: str | None = None
    grado: str | None = Field(None, max_length=20)
    activo: bool | None = None


class CursoResponse(BaseModel):
    cod_curso: str
    nombre_curso: str
    descripcion: str
    grado: str
    activo: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
