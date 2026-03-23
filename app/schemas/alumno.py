"""Alumno schemas."""

from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field


class AlumnoBase(BaseModel):
    cod_alumno: str = Field(..., max_length=20)
    identificacion: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    apellidos: str = Field(..., max_length=100)
    grado: str = Field(..., max_length=20)
    fecha_nacimiento: date
    fecha_ingreso: date
    fecha_egreso: date | None = None
    email: str = Field(default="", max_length=255)
    telefono: str = Field(default="", max_length=30)
    direccion: str = Field(default="", max_length=300)


class AlumnoCreate(AlumnoBase):
    tutor_ids: list[str] = Field(default_factory=list, description="List of cod_tutor to associate")


class AlumnoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    apellidos: str | None = Field(None, max_length=100)
    grado: str | None = Field(None, max_length=20)
    fecha_egreso: date | None = None
    email: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=30)
    direccion: str | None = Field(None, max_length=300)
    tutor_ids: list[str] | None = None


class TutorBrief(BaseModel):
    cod_tutor: str
    nombre: str
    apellidos: str
    parentesco: str

    model_config = {"from_attributes": True}


class AlumnoResponse(BaseModel):
    cod_alumno: str
    identificacion: str
    nombre: str
    apellidos: str
    grado: str
    fecha_nacimiento: date
    fecha_ingreso: date
    fecha_egreso: date | None
    email: str
    telefono: str
    direccion: str
    antiguedad_dias: int | None = None
    tutores: list[TutorBrief] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
