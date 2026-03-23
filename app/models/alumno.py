"""Alumno model and alumno_tutores association table."""

from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ── Association table: alumno ↔ tutor (M:N) ─────────────────

alumno_tutores = Table(
    "alumno_tutores",
    Base.metadata,
    Column("cod_alumno", String(20), ForeignKey("alumnos.cod_alumno", ondelete="CASCADE"), primary_key=True),
    Column("cod_tutor", String(20), ForeignKey("tutores.cod_tutor", ondelete="CASCADE"), primary_key=True),
)


class Alumno(Base):
    __tablename__ = "alumnos"
    __table_args__ = (
        Index("ix_alumnos_identificacion", "identificacion"),
        Index("ix_alumnos_grado", "grado"),
    )

    cod_alumno: Mapped[str] = mapped_column(String(20), primary_key=True)
    identificacion: Mapped[str] = mapped_column(String(512), unique=True, comment="Encrypted PII")
    nombre: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    grado: Mapped[str] = mapped_column(String(20))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    fecha_egreso: Mapped[date | None] = mapped_column(Date, nullable=True)
    email: Mapped[str] = mapped_column(String(512), default="", comment="Encrypted PII")
    telefono: Mapped[str] = mapped_column(String(512), default="", comment="Encrypted PII")
    direccion: Mapped[str] = mapped_column(String(1024), default="", comment="Encrypted PII")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tutores = relationship("Tutor", secondary=alumno_tutores, back_populates="alumnos", lazy="selectin")
    notas = relationship("Nota", back_populates="alumno", lazy="selectin")
    documentos = relationship("DocumentoGenerado", back_populates="alumno", lazy="selectin")
