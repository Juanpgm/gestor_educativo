"""LLM mapper: uses OpenAI to map OCR-extracted text to template variables."""

import json

from openai import AsyncOpenAI

from app.config import get_settings
from app.core.logging import get_logger
from app.models.audit import CostLog

logger = get_logger(__name__)

SYSTEM_PROMPT = """\
You are an expert at extracting structured data from educational documents.
Given raw OCR text from a diploma or grade certificate, extract the relevant
fields and return them as a JSON object.

For diplomas, extract:
- nombre_alumno, identificacion, grado, fecha_graduacion, titulo_otorgado,
  institucion, director, observaciones

For grade certificates (certificado_notas), extract:
- nombre_alumno, identificacion, grado, periodo, notas (array of
  {materia, nota}), promedio, institucion, fecha_emision

Always respond with ONLY valid JSON. No extra text or markdown.
"""


async def map_text_to_variables(
    ocr_text: str,
    document_type: str = "diploma",
    db_session=None,
) -> dict:
    """Use LLM to map OCR-extracted text into template variables."""
    settings = get_settings()
    client = AsyncOpenAI(api_key=settings.openai_api_key)

    user_message = (
        f"Document type: {document_type}\n\n"
        f"OCR extracted text:\n{ocr_text}"
    )

    response = await client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content
    usage = response.usage
    variables = json.loads(content)

    tokens_used = usage.total_tokens if usage else 0
    estimated_cost = (tokens_used / 1000) * 0.002  # gpt-4o-mini approx

    logger.info(
        "llm_mapping_complete",
        document_type=document_type,
        tokens=tokens_used,
        cost=estimated_cost,
    )

    # Log cost if DB session provided
    if db_session:
        cost_log = CostLog(
            operacion="llm_template_mapping",
            costo_estimado=estimated_cost,
            tokens_usados=tokens_used,
            metadata_extra={"model": settings.llm_model, "type": document_type},
        )
        db_session.add(cost_log)

    return variables
