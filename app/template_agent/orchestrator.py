"""Template agent orchestrator: combines OCR → LLM → template filling pipeline."""

from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.template_agent.llm_mapper import map_text_to_variables
from app.template_agent.ocr_processor import extract_text
from app.template_agent.template_builder import fill_template

logger = get_logger(__name__)


async def analyze_and_map_document(
    upload_path: str | Path,
    document_type: str = "diploma",
    lang: str = "spa+eng",
    db_session: AsyncSession | None = None,
) -> dict:
    """
    Pipeline step 1: Extract text from uploaded document and map to variables.

    Args:
        upload_path: Path to uploaded image/PDF of an existing document to analyze.
        document_type: 'diploma' or 'certificado_notas'.
        lang: Tesseract language codes.
        db_session: Optional DB session for cost logging.

    Returns:
        dict of extracted template variables.
    """
    logger.info("agent_pipeline_start", step="ocr", file=str(upload_path))
    ocr_text = extract_text(upload_path, lang)

    logger.info("agent_pipeline_step", step="llm_mapping", chars=len(ocr_text))
    variables = await map_text_to_variables(ocr_text, document_type, db_session)

    logger.info("agent_pipeline_complete", step="mapping", variables=list(variables.keys()))
    return variables


async def generate_from_analysis(
    variables: dict,
    template_path: str | Path,
    output_path: str | Path,
) -> Path:
    """
    Pipeline step 2: Fill a template with the extracted variables.

    Args:
        variables: Dict from analyze_and_map_document.
        template_path: Path to .docx template.
        output_path: Where to save the generated document.

    Returns:
        Path to the generated document.
    """
    return fill_template(template_path, variables, output_path)


async def full_pipeline(
    upload_path: str | Path,
    template_path: str | Path,
    output_path: str | Path,
    document_type: str = "diploma",
    lang: str = "spa+eng",
    db_session: AsyncSession | None = None,
) -> tuple[dict, Path]:
    """
    Complete pipeline: OCR → LLM mapping → template fill.

    Returns:
        Tuple of (extracted variables dict, output file path).
    """
    variables = await analyze_and_map_document(
        upload_path, document_type, lang, db_session
    )
    result_path = await generate_from_analysis(variables, template_path, output_path)
    return variables, result_path
