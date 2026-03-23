"""Nota (grade) model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Nota(Base):
    __tablename__ = "notas"
    __table_args__ = (
        UniqueConstraint("cod_alumno", "cod_materia", "cod_periodo", name="uq_nota_alumno_materia_periodo"),
        Index("ix_notas_alumno_periodo", "cod_alumno", "cod_periodo"),
        Index("ix_notas_materia", "cod_materia"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cod_alumno: Mapped[str] = mapped_column(
        String(20), ForeignKey("alumnos.cod_alumno", ondelete="CASCADE")
    )
    cod_materia: Mapped[str] = mapped_column(
        String(20), ForeignKey("materias.cod_materia", ondelete="CASCADE")
    )
    cod_periodo: Mapped[str] = mapped_column(
        String(20), ForeignKey("periodos_academicos.cod_periodo", ondelete="CASCADE")
    )
    nota: Mapped[float] = mapped_column(Numeric(4, 2), comment="Grade value 0.00-10.00")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    alumno = relationship("Alumno", back_populates="notas")
    materia = relationship("Materia", back_populates="notas")
    periodo = relationship("PeriodoAcademico", back_populates="notas")
