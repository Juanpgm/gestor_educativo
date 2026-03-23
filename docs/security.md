# Security

## PII Encryption

Sensitive fields are encrypted at rest using Fernet (AES-128-CBC):

| Model   | Encrypted Fields                           |
| ------- | ------------------------------------------ |
| Alumno  | identificacion, email, telefono, direccion |
| Docente | identificacion, email, telefono, direccion |
| Tutor   | identificacion, email, telefono, direccion |

- **Encryption**: `encrypt_value(plaintext)` before DB insert
- **Decryption**: `decrypt_value(ciphertext)` when building API response
- **Key**: `ENCRYPTION_KEY` in environment (Fernet key format)

## Authentication & Authorization

- JWT tokens with HS256 signing
- Password hashing: bcrypt (via passlib)
- Role-based access control: admin, secretaria, docente
- Token expiration: 30min access, 7 days refresh

## Rate Limiting

In-memory per-IP rate limiting:

- General endpoints: 100 requests/minute
- Login endpoint: 5 requests/minute (brute-force protection)

## Security Headers

Applied via middleware on all responses:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`

## CORS

Configurable allowed origins via `ALLOWED_ORIGINS` env variable.

## SQL Injection Prevention

SQLAlchemy ORM exclusively — no raw SQL queries anywhere in the codebase.

## File Upload Validation

Template uploads are restricted to .docx files and saved to controlled directories.

## Logging

- Structured JSON logs in production
- Request audit trail with UUID per request
- PII values are NEVER logged — only encrypted forms

## Dependencies

- `pip-audit` configured for vulnerability scanning
- Run `make audit` to check for known CVEs
