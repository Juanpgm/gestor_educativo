"""Email API: send documents via Gmail."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AdminOrSecretaria, DB
from app.models.documento import DocumentoGenerado
from app.schemas.documento import EnviarEmailRequest
from app.services.email_service import send_email

router = APIRouter(prefix="/email", tags=["Email"])


@router.post("/enviar")
async def enviar_documento(db: DB, data: EnviarEmailRequest, user: AdminOrSecretaria):
    """Send a generated document to a recipient via Gmail API."""
    result = await db.execute(
        select(DocumentoGenerado).where(DocumentoGenerado.id == data.documento_id)
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Documento not found")

    try:
        email_result = await send_email(
            to=data.destinatario,
            subject=data.asunto,
            body_html=data.cuerpo_html,
            attachment_path=doc.archivo_path,
        )
        return {"status": "sent", **email_result}
    except FileNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Email send failed: {e}")
