"""Docente model and docente_materias association table."""

from datetime import date, datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    String,
    Table,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# ── Association table: docente ↔ materia (M:N) ──────────────

docente_materias = Table(
    "docente_materias",
    Base.metadata,
    Column("cod_docente", String(20), ForeignKey("docentes.cod_docente", ondelete="CASCADE"), primary_key=True),
    Column("cod_materia", String(20), ForeignKey("materias.cod_materia", ondelete="CASCADE"), primary_key=True),
    Column("cod_periodo", String(20), ForeignKey("periodos_academicos.cod_periodo", ondelete="CASCADE"), primary_key=True),
)


class Docente(Base):
    __tablename__ = "docentes"

    cod_docente: Mapped[str] = mapped_column(String(20), primary_key=True)
    identificacion: Mapped[str] = mapped_column(String(512), unique=True, comment="Encrypted PII")
    nombre: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
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
    materias = relationship("Materia", secondary=docente_materias, back_populates="docentes", lazy="selectin")
