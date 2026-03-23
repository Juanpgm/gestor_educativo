# Skill: Document Generation

## Description

Generate educational documents (diplomas, grade certificates) from .docx templates.

## Pipeline

1. **OCR** (optional): Extract text from uploaded documents using Tesseract
2. **LLM Mapping**: Map extracted text to template variables via OpenAI API
3. **Template Fill**: Render .docx templates using docxtpl (Jinja2 syntax)
4. **Certification**: Generate SHA-256 hash + QR code for verification
5. **Delivery**: Send generated documents via Gmail API

## Key Files

- `app/template_agent/orchestrator.py` — Full pipeline coordinator
- `app/template_agent/ocr_processor.py` — Tesseract OCR extraction
- `app/template_agent/llm_mapper.py` — OpenAI variable mapping
- `app/template_agent/template_builder.py` — docxtpl rendering
- `app/services/certification_service.py` — Hash + QR generation
- `app/services/document_service.py` — Document generation orchestrator
- `app/services/email_service.py` — Gmail API integration
