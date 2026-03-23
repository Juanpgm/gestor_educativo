#!/bin/sh
set -e

echo "══════════════════════════════════════════════════"
echo "  Gestor Educativo — Starting deployment"
echo "══════════════════════════════════════════════════"

# ── 1. Run Alembic migrations ────────────────────────────────
echo "→ Running Alembic migrations..."
if alembic upgrade head; then
    echo "✅ Migrations completed successfully"
else
    echo "❌ Migrations failed! Check DATABASE_URL and database connectivity."
    echo "   DATABASE_URL starts with: $(echo $DATABASE_URL | cut -c1-30)..."
    exit 1
fi

# ── 2. Seed test data (non-blocking) ─────────────────────────
echo "→ Running seed script..."
if python scripts/seed_data.py; then
    echo "✅ Seed completed"
else
    echo "⚠️  Seed failed (non-critical, continuing startup)"
fi

# ── 3. Start uvicorn ─────────────────────────────────────────
echo "→ Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
