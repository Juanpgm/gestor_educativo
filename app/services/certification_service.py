"""Certification service: SHA-256 hash + QR code generation + verification."""

import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path

import qrcode

from app.config import get_settings


def generate_document_hash(
    alumno_id: str,
    tipo_documento: str,
    contenido_json: dict,
) -> str:
    """Generate a SHA-256 hash for document verification."""
    payload = json.dumps(
        {
            "alumno_id": alumno_id,
            "tipo": tipo_documento,
            "contenido": contenido_json,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_qr_code(hash_verificacion: str, output_path: str | Path) -> Path:
    """Generate a QR code PNG containing the verification URL."""
    settings = get_settings()
    verification_url = (
        f"{settings.base_url}/api/v1/documentos/verificar/{hash_verificacion}"
    )

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10)
    qr.add_data(verification_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path))
    return output_path


def generate_qr_bytes(hash_verificacion: str) -> bytes:
    """Generate a QR code as PNG bytes (for embedding in documents)."""
    settings = get_settings()
    verification_url = (
        f"{settings.base_url}/api/v1/documentos/verificar/{hash_verificacion}"
    )

    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8)
    qr.add_data(verification_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
