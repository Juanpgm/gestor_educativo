"""Documentos API: generation, verification, template management, and agent pipeline."""

import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from sqlalchemy import select

from app.api.deps import AdminOrSecretaria, CurrentUser, DB
from app.config import get_settings
from app.models.documento import DocumentoGenerado
from app.models.plantilla import Plantilla
from app.schemas.documento import (
    DocumentoResponse,
    GeneracionMasivaResponse,
    GenerarDocumentoRequest,
    PlantillaResponse,
    VerificacionResponse,
)
from app.services.document_service import generate_bulk, generate_document
from app.template_agent.orchestrator import analyze_and_map_document
from app.template_agent.template_builder import list_template_variables

router = APIRouter(prefix="/documentos", tags=["Documentos"])


# ── Plantillas ───────────────────────────────────────────────

@router.get("/plantillas", response_model=list[PlantillaResponse])
async def list_plantillas(db: DB, user: CurrentUser):
    result = await db.execute(select(Plantilla))
    return result.scalars().all()


@router.post("/plantillas/upload", response_model=PlantillaResponse, status_code=status.HTTP_201_CREATED)
async def upload_plantilla(
    db: DB,
    user: AdminOrSecretaria,
    file: UploadFile,
    nombre: str = Query(...),
    tipo: str = Query(..., pattern="^(diploma|certificado_notas)$"),
    idioma: str = Query("es", pattern="^(es|en)$"),
    descripcion: str = Query(""),
):
    settings = get_settings()
    template_dir = Path(settings.templates_dir) / tipo
    template_dir.mkdir(parents=True, exist_ok=True)
    dest = template_dir / file.filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    variables = list_template_variables(dest)

    plantilla = Plantilla(
        nombre=nombre,
        tipo=tipo,
        idioma=idioma,
        archivo_template_path=str(dest),
        variables_mapeadas=variables,
        descripcion=descripcion,
    )
    db.add(plantilla)
    await db.flush()
    await db.refresh(plantilla)
    return plantilla


# ── Generation ───────────────────────────────────────────────

@router.post("/generar", response_model=DocumentoResponse, status_code=status.HTTP_201_CREATED)
async def generar_documento(db: DB, data: GenerarDocumentoRequest, user: AdminOrSecretaria):
    try:
        doc = await generate_document(
            db, data.cod_alumno, data.plantilla_id, data.cod_periodo
        )
        return doc
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@router.post("/generar/masivo", response_model=GeneracionMasivaResponse, status_code=status.HTTP_201_CREATED)
async def generar_masivo(
    db: DB,
    user: AdminOrSecretaria,
    plantilla_id: int = Query(...),
    cod_alumnos: str = Query(..., description="Comma-separated student codes"),
    cod_periodo: str | None = Query(None),
):
    """Mass generation for a list of students."""
    codes = [c.strip() for c in cod_alumnos.split(",")]
    docs = await generate_bulk(db, codes, plantilla_id, cod_periodo)
    return GeneracionMasivaResponse(
        total_solicitados=len(codes),
        total_generados=len(docs),
        documentos=docs,
    )


# ── Verification ─────────────────────────────────────────────

@router.get("/verificar/{hash_verificacion}", response_model=VerificacionResponse)
async def verificar_documento(db: DB, hash_verificacion: str):
    """Public endpoint: verify a document by its hash (no auth required)."""
    result = await db.execute(
        select(DocumentoGenerado).where(DocumentoGenerado.hash_verificacion == hash_verificacion)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        return VerificacionResponse(valido=False, mensaje="Documento no encontrado")
    return VerificacionResponse(
        valido=True,
        mensaje="Documento verificado exitosamente",
        tipo_documento=doc.tipo.value,
        cod_alumno=doc.cod_alumno,
        fecha_generacion=doc.fecha_generacion,
    )


# ── Listing ──────────────────────────────────────────────────

@router.get("", response_model=list[DocumentoResponse])
async def list_documentos(
    db: DB,
    user: CurrentUser,
    cod_alumno: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    stmt = select(DocumentoGenerado)
    if cod_alumno:
        stmt = stmt.where(DocumentoGenerado.cod_alumno == cod_alumno)
    result = await db.execute(
        stmt.order_by(DocumentoGenerado.fecha_generacion.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


# ── Template Agent (OCR + LLM) ───────────────────────────────

@router.post("/analizar")
async def analizar_documento(
    db: DB,
    user: AdminOrSecretaria,
    file: UploadFile,
    tipo: str = Query("diploma", pattern="^(diploma|certificado_notas)$"),
    idioma: str = Query("spa+eng"),
):
    """Upload an existing document (image/PDF) to extract variables via OCR + LLM."""
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest = upload_dir / f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{file.filename}"
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        variables = await analyze_and_map_document(dest, tipo, idioma, db)
        return {"status": "success", "variables": variables, "uploaded_file": str(dest)}
    except Exception as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Analysis failed: {e}")
