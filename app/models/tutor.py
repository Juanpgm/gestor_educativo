"""Tutor model."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.alumno import alumno_tutores


class Tutor(Base):
    __tablename__ = "tutores"

    cod_tutor: Mapped[str] = mapped_column(String(20), primary_key=True)
    identificacion: Mapped[str] = mapped_column(String(512), unique=True, comment="Encrypted PII")
    nombre: Mapped[str] = mapped_column(String(100))
    apellidos: Mapped[str] = mapped_column(String(100))
    parentesco: Mapped[str] = mapped_column(String(50))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(512), default="", comment="Encrypted PII")
    telefono: Mapped[str] = mapped_column(String(512), default="", comment="Encrypted PII")
    direccion: Mapped[str] = mapped_column(String(1024), default="", comment="Encrypted PII")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    alumnos = relationship("Alumno", secondary=alumno_tutores, back_populates="tutores", lazy="selectin")
