"""Materia model and materia_grados association table."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.docente import docente_materias

# ── Association table: materia ↔ grados ──────────────────────

materia_grados = Table(
    "materia_grados",
    Base.metadata,
    Column("cod_materia", String(20), ForeignKey("materias.cod_materia", ondelete="CASCADE"), primary_key=True),
    Column("grado", String(20), primary_key=True),
)


class Materia(Base):
    __tablename__ = "materias"

    cod_materia: Mapped[str] = mapped_column(String(20), primary_key=True)
    nombre_materia: Mapped[str] = mapped_column(String(150))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    docentes = relationship("Docente", secondary=docente_materias, back_populates="materias", lazy="selectin")
    grados = relationship("MateriaGradoView", back_populates="materia", lazy="selectin", viewonly=True)
    notas = relationship("Nota", back_populates="materia", lazy="selectin")


class MateriaGradoView(Base):
    """Read-only model to access materia_grados rows for relationship."""

    __tablename__ = "materia_grados"
    __table_args__ = {"extend_existing": True}

    cod_materia: Mapped[str] = mapped_column(
        String(20), ForeignKey("materias.cod_materia"), primary_key=True
    )
    grado: Mapped[str] = mapped_column(String(20), primary_key=True)

    materia = relationship("Materia", back_populates="grados", viewonly=True)
