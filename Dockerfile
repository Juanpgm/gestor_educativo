# ── Stage 1: Build ─────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: Runtime ───────────────────────────────────────────
FROM python:3.11-slim

# System deps for Tesseract OCR + Poppler (pdf2image)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    libmagic1 && \
    rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /install /usr/local

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

WORKDIR /app

# Copy ALL application code in one layer (ensures cache invalidation)
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY pyproject.toml .
COPY scripts/ ./scripts/
COPY templates/ ./templates/

# Create runtime directories & make start script executable
RUN mkdir -p templates/diplomas templates/certificados uploads generated && \
    chmod +x scripts/start.sh && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["sh", "scripts/start.sh"]
