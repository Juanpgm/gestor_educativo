"""Document generation service: orchestrates template filling, certification, and storage."""

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging import get_logger
from app.models.alumno import Alumno
from app.models.documento import DocumentoGenerado
from app.models.nota import Nota
from app.models.periodo import PeriodoAcademico
from app.models.plantilla import Plantilla
from app.services.certification_service import generate_document_hash, generate_qr_code
from app.template_agent.template_builder import fill_template
from app.utils.encryption import decrypt_value

logger = get_logger(__name__)


async def _load_alumno(db: AsyncSession, cod_alumno: str) -> Alumno:
    result = await db.execute(select(Alumno).where(Alumno.cod_alumno == cod_alumno))
    alumno = result.scalar_one_or_none()
    if not alumno:
        raise ValueError(f"Alumno '{cod_alumno}' not found")
    return alumno


async def _load_notas(db: AsyncSession, cod_alumno: str, cod_periodo: str | None = None):
    stmt = (
        select(Nota)
        .where(Nota.cod_alumno == cod_alumno)
    )
    if cod_periodo:
        stmt = stmt.where(Nota.cod_periodo == cod_periodo)
    result = await db.execute(stmt)
    return result.scalars().all()


async def generate_document(
    db: AsyncSession,
    cod_alumno: str,
    plantilla_id: int,
    cod_periodo: str | None = None,
) -> DocumentoGenerado:
    """Generate a single document (diploma or grade certificate) for a student."""
    settings = get_settings()

    # Load entities
    alumno = await _load_alumno(db, cod_alumno)
    result = await db.execute(select(Plantilla).where(Plantilla.id == plantilla_id))
    plantilla = result.scalar_one_or_none()
    if not plantilla:
        raise ValueError(f"Plantilla with id={plantilla_id} not found")

    # Build context for template
    context = {
        "nombre_alumno": f"{alumno.nombre} {alumno.apellidos}",
        "identificacion": decrypt_value(alumno.identificacion),
        "grado": alumno.grado or "",
        "fecha_ingreso": str(alumno.fecha_ingreso) if alumno.fecha_ingreso else "",
        "fecha_generacion": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "institucion": settings.app_name,
    }

    # Load notas if grade certificate
    if plantilla.tipo.value == "certificado_notas":
        notas = await _load_notas(db, cod_alumno, cod_periodo)
        context["notas"] = [
            {"materia": n.cod_materia, "nota": float(n.nota), "periodo": n.cod_periodo}
            for n in notas
        ]
        if cod_periodo:
            result = await db.execute(
                select(PeriodoAcademico).where(PeriodoAcademico.cod_periodo == cod_periodo)
            )
            periodo = result.scalar_one_or_none()
            context["periodo"] = periodo.nombre if periodo else cod_periodo

    # Generate verification hash
    hash_verificacion = generate_document_hash(cod_alumno, plantilla.tipo.value, context)

    # Generate QR code
    qr_path = Path(settings.generated_dir) / f"qr_{hash_verificacion[:12]}.png"
    generate_qr_code(hash_verificacion, qr_path)
    context["qr_path"] = str(qr_path)
    context["hash_verificacion"] = hash_verificacion

    # Fill template
    template_path = Path(plantilla.archivo_template_path)
    output_filename = f"{plantilla.tipo.value}_{cod_alumno}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.docx"
    output_path = Path(settings.generated_dir) / output_filename
    fill_template(str(template_path), context, str(output_path))

    # Persist to DB
    doc = DocumentoGenerado(
        cod_alumno=cod_alumno,
        tipo=plantilla.tipo,
        archivo_path=str(output_path),
        hash_verificacion=hash_verificacion,
        qr_data=str(qr_path),
        metadata_doc=context,
    )
    db.add(doc)
    await db.flush()
    await db.refresh(doc)

    logger.info(
        "document_generated",
        cod_alumno=cod_alumno,
        tipo=plantilla.tipo.value,
        doc_id=doc.id,
    )
    return doc


async def generate_bulk(
    db: AsyncSession,
    cod_alumnos: list[str],
    plantilla_id: int,
    cod_periodo: str | None = None,
) -> list[DocumentoGenerado]:
    """Generate documents for multiple students."""
    results = []
    errors = []
    for cod in cod_alumnos:
        try:
            doc = await generate_document(db, cod, plantilla_id, cod_periodo)
            results.append(doc)
        except Exception as e:
            logger.error("bulk_generation_error", cod_alumno=cod, error=str(e))
            errors.append({"cod_alumno": cod, "error": str(e)})
    if errors:
        logger.warning("bulk_generation_completed_with_errors", errors=errors)
    return results
