# Certification System

## Overview

Every generated document receives a unique SHA-256 hash and QR code for verification. The verification endpoint is public (no authentication required).

## How It Works

1. **Hash Generation**: SHA-256 of `{alumno_id, tipo_documento, contenido_json, timestamp}`
2. **QR Code**: Contains URL to verification endpoint with the hash
3. **Storage**: Hash stored in `documentos_generados.hash_verificacion` (unique index)

## Verification Flow

```
QR Code Scan → GET /api/v1/documentos/verificar/{hash}
    │
    ├── Found → { valido: true, tipo_documento, cod_alumno, fecha_generacion }
    └── Not Found → { valido: false, mensaje: "Documento no encontrado" }
```

## API

```
GET /api/v1/documentos/verificar/a1b2c3d4e5f6...
```

Response (valid):

```json
{
  "valido": true,
  "mensaje": "Documento verificado exitosamente",
  "tipo_documento": "diploma",
  "cod_alumno": "ALU001",
  "fecha_generacion": "2024-01-15T10:30:00Z"
}
```

## Security Notes

- Hash is SHA-256 (256-bit), collision-resistant
- Timestamp included to ensure uniqueness even for identical data
- QR code uses ERROR_CORRECT_M (15% error recovery)
- Verification endpoint is public for external validators
- No PII is exposed in verification response (only cod_alumno)
