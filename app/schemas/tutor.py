"""Tutor schemas."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class TutorBase(BaseModel):
    cod_tutor: str = Field(..., max_length=20)
    identificacion: str = Field(..., max_length=50)
    nombre: str = Field(..., max_length=100)
    apellidos: str = Field(..., max_length=100)
    parentesco: str = Field(..., max_length=50)
    fecha_nacimiento: date
    email: str = Field(default="", max_length=255)
    telefono: str = Field(default="", max_length=30)
    direccion: str = Field(default="", max_length=300)


class TutorCreate(TutorBase):
    pass


class TutorUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    apellidos: str | None = Field(None, max_length=100)
    parentesco: str | None = Field(None, max_length=50)
    email: str | None = Field(None, max_length=255)
    telefono: str | None = Field(None, max_length=30)
    direccion: str | None = Field(None, max_length=300)


class TutorResponse(BaseModel):
    cod_tutor: str
    identificacion: str
    nombre: str
    apellidos: str
    parentesco: str
    fecha_nacimiento: date
    email: str
    telefono: str
    direccion: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
