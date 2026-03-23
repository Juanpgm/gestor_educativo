"""Docente schemas."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class DocenteBase(BaseModel):
    cod_docente: str = Field(..., max_length=20)
    identificacion: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    apellidos: str = Field(..., max_length=100)
    fecha_nacimiento: date
    fecha_ingreso: date
    fecha_egreso: date | None = None
    email: str = Field(default="", max_length=255)
    telefono: str = Field(default="", max_length=30)
    direccion: str = Field(default="", max_length=300)


class DocenteCreate(DocenteBase):
    materia_ids: list[str] = Field(default_factory=list, description="List of cod_materia")


class DocenteUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    apellidos: str | None = Field(None, max_length=100)
    fecha_egreso: date | None = None
    email: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=30)
    direccion: str | None = Field(None, max_length=300)
    materia_ids: list[str] | None = None


class DocenteResponse(BaseModel):
    cod_docente: str
    identificacion: str
    nombre: str
    apellidos: str
    fecha_nacimiento: date
    fecha_ingreso: date
    fecha_egreso: date | None
    email: str
    telefono: str
    direccion: str
    antiguedad_dias: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
