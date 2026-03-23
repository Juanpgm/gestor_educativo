"""Documento and Plantilla schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.documento import TipoDocumento
from app.models.plantilla import IdiomaPlantilla, TipoPlantilla


# ── Plantilla ────────────────────────────────────────────────


class PlantillaResponse(BaseModel):
    id: int
    nombre: str
    tipo: TipoPlantilla
    idioma: IdiomaPlantilla
    archivo_template_path: str
    variables_mapeadas: dict | None = None
    descripcion: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Documento ────────────────────────────────────────────────


class GenerarDocumentoRequest(BaseModel):
    plantilla_id: int
    cod_alumno: str = Field(..., max_length=20)
    cod_periodo: str | None = None


class DocumentoResponse(BaseModel):
    id: int
    tipo: TipoDocumento
    cod_alumno: str
    hash_verificacion: str
    archivo_path: str
    fecha_generacion: datetime
    metadata_doc: dict | None = None

    model_config = {"from_attributes": True}


class VerificacionResponse(BaseModel):
    valido: bool
    mensaje: str
    tipo_documento: str | None = None
    cod_alumno: str | None = None
    fecha_generacion: datetime | None = None


class GeneracionMasivaResponse(BaseModel):
    total_solicitados: int
    total_generados: int
    documentos: list[DocumentoResponse] = []


# ── Email ────────────────────────────────────────────────────


class EnviarEmailRequest(BaseModel):
    documento_id: int
    destinatario: str = Field(..., max_length=255)
    asunto: str = Field(default="Documento académico")
    cuerpo_html: str = Field(default="<p>Adjunto encontrará su documento académico.</p>")
