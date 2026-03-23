"""Audit and Cost log models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    accion: Mapped[str] = mapped_column(String(50))
    entidad: Mapped[str] = mapped_column(String(50))
    entidad_id: Mapped[str] = mapped_column(String(50), default="")
    detalles: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip: Mapped[str] = mapped_column(String(45), default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CostLog(Base):
    __tablename__ = "cost_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    operacion: Mapped[str] = mapped_column(String(100))
    detalle: Mapped[str] = mapped_column(Text, default="")
    costo_estimado: Mapped[float] = mapped_column(Numeric(10, 6), default=0)
    tokens_usados: Mapped[int] = mapped_column(Integer, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
