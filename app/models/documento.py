"""DocumentoGenerado model for certified documents."""

import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TipoDocumento(str, enum.Enum):
    diploma = "diploma"
    certificado_notas = "certificado_notas"


class DocumentoGenerado(Base):
    __tablename__ = "documentos_generados"
    __table_args__ = (
        Index("ix_documentos_hash", "hash_verificacion", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tipo: Mapped[TipoDocumento] = mapped_column(Enum(TipoDocumento))
    cod_alumno: Mapped[str] = mapped_column(
        String(20), ForeignKey("alumnos.cod_alumno", ondelete="CASCADE")
    )
    hash_verificacion: Mapped[str] = mapped_column(String(64), unique=True, comment="SHA-256 hex")
    qr_data: Mapped[str] = mapped_column(Text, default="")
    archivo_path: Mapped[str] = mapped_column(String(500))
    metadata_doc: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    fecha_generacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    alumno = relationship("Alumno", back_populates="documentos")
