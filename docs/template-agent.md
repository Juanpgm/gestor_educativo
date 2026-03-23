# Template Agent

## Overview

The template agent is an OCR + LLM pipeline that analyzes uploaded documents (images or PDFs of existing diplomas/certificates) and extracts structured data to map into template variables.

## Pipeline

```
Upload (image/PDF)
    │
    ▼
┌─────────────────┐
│  OCR Processor   │  Tesseract (pytesseract + pdf2image)
│  → Raw text      │  Supports: PNG, JPG, TIFF, BMP, PDF
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Mapper      │  OpenAI API (gpt-4o-mini default)
│  → JSON variables │  Structured JSON output
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Template Builder  │  docxtpl (Jinja2 .docx)
│  → Generated doc  │
└─────────────────┘
```

## Usage

### Step 1: Analyze document

```
POST /api/v1/documentos/analizar
Content-Type: multipart/form-data
file: <existing_diploma.pdf>
tipo: diploma
idioma: spa+eng
```

Response:

```json
{
    "status": "success",
    "variables": {
        "nombre_alumno": "Juan Pérez",
        "identificacion": "1234567890",
        "grado": "11°",
        "titulo_otorgado": "Bachiller Académico",
        ...
    }
}
```

### Step 2: Use variables in template generation

The extracted variables can be used to create new templates or verify data.

## Configuration

| Setting        | Default     | Description                   |
| -------------- | ----------- | ----------------------------- |
| OPENAI_API_KEY | (required)  | OpenAI API key                |
| LLM_MODEL      | gpt-4o-mini | Model for variable extraction |

## Cost Tracking

Every LLM call is logged in the `cost_log` table with:

- Operation name
- Token count (input + output)
- Estimated cost (USD)
- Model used

## Supported Input Formats

| Format              | Engine                         |
| ------------------- | ------------------------------ |
| PNG, JPG, TIFF, BMP | Tesseract OCR directly         |
| PDF                 | pdf2image → Tesseract per page |

## Language Support

Tesseract requires language packs. Installed in Docker:

- `tesseract-ocr-spa` (Spanish)
- `tesseract-ocr-eng` (English)

Use `idioma` parameter: `spa`, `eng`, or `spa+eng` (both).
