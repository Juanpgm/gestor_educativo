# Document Generation

## Overview

The system generates .docx documents (diplomas and grade certificates) from templates using the docxtpl library (Jinja2 syntax).

## Single Generation

```json
POST /api/v1/documentos/generar
Authorization: Bearer <token>
{
    "cod_alumno": "ALU001",
    "plantilla_id": 1,
    "cod_periodo": "2024-1"  // optional, for grade certificates
}
```

The system:

1. Loads student data and decrypts PII
2. Loads grades (for certificado_notas type)
3. Generates SHA-256 hash for verification
4. Generates QR code with verification URL
5. Fills .docx template with context variables
6. Saves to `generated/` directory
7. Persists record in `documentos_generados` table

## Mass Generation

Send comma-separated student codes:

```json
POST /api/v1/documentos/generar/masivo
{
    "cod_alumnos": ["ALU001", "ALU002", "ALU003"],
    "plantilla_id": 1
}
```

## Template Variables

Templates use Jinja2 syntax (`{{ variable_name }}`). Common variables:

| Variable            | Description                       |
| ------------------- | --------------------------------- |
| `nombre_alumno`     | Full name                         |
| `identificacion`    | Decrypted ID                      |
| `grado`             | Grade level                       |
| `fecha_ingreso`     | Enrollment date                   |
| `fecha_generacion`  | Generation date                   |
| `institucion`       | Institution name                  |
| `notas`             | Array of {materia, nota, periodo} |
| `periodo`           | Academic period name              |
| `qr_path`           | Path to verification QR code      |
| `hash_verificacion` | SHA-256 hash                      |

## Uploading Templates

```
POST /api/v1/documentos/plantillas/upload
Content-Type: multipart/form-data
file: <template.docx>
nombre: Diploma Español
tipo: diploma
idioma: es
descripcion: Plantilla diploma en español
```
