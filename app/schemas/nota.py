"""Nota (grade) schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class NotaBase(BaseModel):
    cod_alumno: str = Field(..., max_length=20)
    cod_materia: str = Field(..., max_length=20)
    cod_periodo: str = Field(..., max_length=20)
    nota: float = Field(..., ge=0.00, le=10.00, description="Grade value 0.00-10.00")


class NotaCreate(NotaBase):
    pass


class NotaBulkCreate(BaseModel):
    notas: list[NotaCreate]


class NotaUpdate(BaseModel):
    nota: float = Field(..., ge=0.00, le=10.00)


class NotaResponse(BaseModel):
    id: int
    cod_alumno: str
    cod_materia: str
    cod_periodo: str
    nota: float
    nombre_alumno: str | None = None
    nombre_materia: str | None = None
    nombre_periodo: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PeriodoBase(BaseModel):
    cod_periodo: str = Field(..., max_length=20)
    nombre: str = Field(..., max_length=100)
    anio: int
    fecha_inicio: datetime
    fecha_fin: datetime
    activo: bool = True


class PeriodoCreate(PeriodoBase):
    pass


class PeriodoUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=100)
    anio: int | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    activo: bool | None = None


class PeriodoResponse(BaseModel):
    cod_periodo: str
    nombre: str
    anio: int
    fecha_inicio: datetime
    fecha_fin: datetime
    activo: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
