"""Template builder: fills .docx templates with context variables using docxtpl."""

from pathlib import Path

from docxtpl import DocxTemplate

from app.core.logging import get_logger

logger = get_logger(__name__)


def fill_template(
    template_path: str | Path,
    context: dict,
    output_path: str | Path,
) -> Path:
    """Fill a .docx template with the given context and save to output_path."""
    template_path = Path(template_path)
    output_path = Path(output_path)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = DocxTemplate(str(template_path))

    # docxtpl uses Jinja2 syntax: {{ variable_name }}
    doc.render(context)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))

    logger.info(
        "template_filled",
        template=str(template_path),
        output=str(output_path),
        variables=list(context.keys()),
    )
    return output_path


def list_template_variables(template_path: str | Path) -> list[str]:
    """List all Jinja2 variables found in a .docx template."""
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    doc = DocxTemplate(str(template_path))
    return list(doc.get_undeclared_template_variables())
