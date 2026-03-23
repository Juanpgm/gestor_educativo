"""Plantilla model for document templates."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TipoPlantilla(str, enum.Enum):
    diploma = "diploma"
    certificado_notas = "certificado_notas"


class IdiomaPlantilla(str, enum.Enum):
    es = "es"
    en = "en"


class Plantilla(Base):
    __tablename__ = "plantillas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(200))
    tipo: Mapped[TipoPlantilla] = mapped_column(Enum(TipoPlantilla))
    idioma: Mapped[IdiomaPlantilla] = mapped_column(Enum(IdiomaPlantilla), default=IdiomaPlantilla.es)
    archivo_template_path: Mapped[str] = mapped_column(String(500))
    archivo_original_path: Mapped[str] = mapped_column(String(500), default="")
    variables_mapeadas: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    descripcion: Mapped[str] = mapped_column(Text, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
