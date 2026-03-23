"""OCR processor: extract text from uploaded document images/PDFs using Tesseract."""

from pathlib import Path

import pytesseract
from PIL import Image

from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_image(image_path: str | Path, lang: str = "spa+eng") -> str:
    """Extract text from a single image file using Tesseract OCR."""
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=lang)
    logger.info("ocr_extraction", file=str(image_path), chars=len(text))
    return text


def extract_text_from_pdf(pdf_path: str | Path, lang: str = "spa+eng") -> str:
    """Extract text from a PDF by converting pages to images, then running OCR."""
    from pdf2image import convert_from_path

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    images = convert_from_path(str(pdf_path), dpi=300)
    all_text = []
    for i, img in enumerate(images):
        page_text = pytesseract.image_to_string(img, lang=lang)
        all_text.append(f"--- Page {i + 1} ---\n{page_text}")

    combined = "\n".join(all_text)
    logger.info("ocr_pdf_extraction", file=str(pdf_path), pages=len(images), chars=len(combined))
    return combined


def extract_text(file_path: str | Path, lang: str = "spa+eng") -> str:
    """Auto-detect file type and extract text via OCR."""
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path, lang)
    if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return extract_text_from_image(file_path, lang)
    raise ValueError(f"Unsupported file type: {suffix}")
