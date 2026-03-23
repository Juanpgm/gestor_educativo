"""Tests for Documentos API endpoints (plantillas, generation, verification)."""

from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alumno import Alumno
from app.models.documento import DocumentoGenerado, TipoDocumento
from app.models.plantilla import Plantilla, TipoPlantilla, IdiomaPlantilla
from app.utils.encryption import encrypt_value


@pytest_asyncio.fixture
async def seed_plantilla(db_session: AsyncSession) -> Plantilla:
    """Create a test plantilla in DB."""
    plantilla = Plantilla(
        nombre="Diploma Test",
        tipo=TipoPlantilla.diploma,
        idioma=IdiomaPlantilla.es,
        archivo_template_path="templates/diplomas/test.docx",
        variables_mapeadas={"nombre_alumno": "string", "grado": "string"},
        descripcion="Test diploma template",
    )
    db_session.add(plantilla)
    await db_session.commit()
    await db_session.refresh(plantilla)
    return plantilla


@pytest_asyncio.fixture
async def seed_alumno(db_session: AsyncSession) -> Alumno:
    """Create a test alumno in DB."""
    alumno = Alumno(
        cod_alumno="ALU001",
        identificacion=encrypt_value("1234567890"),
        nombre="Juan",
        apellidos="Pérez",
        grado="10",
        fecha_nacimiento=date(2008, 5, 15),
        fecha_ingreso=date(2023, 1, 15),
    )
    db_session.add(alumno)
    await db_session.commit()
    await db_session.refresh(alumno)
    return alumno


@pytest_asyncio.fixture
async def seed_documento(db_session: AsyncSession, seed_alumno) -> DocumentoGenerado:
    """Create a test generated document in DB."""
    doc = DocumentoGenerado(
        tipo=TipoDocumento.diploma,
        cod_alumno="ALU001",
        hash_verificacion="a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
        qr_data="generated/qr_test.png",
        archivo_path="generated/diploma_ALU001_test.docx",
        metadata_doc={"nombre_alumno": "Juan Pérez", "grado": "10"},
    )
    db_session.add(doc)
    await db_session.commit()
    await db_session.refresh(doc)
    return doc


# ── Plantillas ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_plantillas_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/documentos/plantillas", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_plantillas(client: AsyncClient, auth_headers, seed_plantilla):
    response = await client.get("/api/v1/documentos/plantillas", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Diploma Test"
    assert data[0]["tipo"] == "diploma"
    assert data[0]["idioma"] == "es"


@pytest.mark.asyncio
async def test_list_plantillas_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/documentos/plantillas")
    assert response.status_code in (401, 403)


# ── Verification ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_verificar_documento_valid(client: AsyncClient, seed_documento):
    """Verification endpoint is public (no auth required)."""
    hash_val = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
    response = await client.get(f"/api/v1/documentos/verificar/{hash_val}")
    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is True
    assert data["mensaje"] == "Documento verificado exitosamente"
    assert data["tipo_documento"] == "diploma"
    assert data["cod_alumno"] == "ALU001"
    assert data["fecha_generacion"] is not None


@pytest.mark.asyncio
async def test_verificar_documento_not_found(client: AsyncClient):
    """Non-existent hash returns valido=False."""
    response = await client.get("/api/v1/documentos/verificar/nonexistenthash123")
    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is False
    assert "no encontrado" in data["mensaje"].lower()


@pytest.mark.asyncio
async def test_verificar_no_auth_required(client: AsyncClient):
    """Verification endpoint should work without authentication."""
    response = await client.get("/api/v1/documentos/verificar/anyhash")
    assert response.status_code == 200


# ── List Documentos ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_documentos_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/documentos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_documentos(client: AsyncClient, auth_headers, seed_documento):
    response = await client.get("/api/v1/documentos", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cod_alumno"] == "ALU001"
    assert data[0]["tipo"] == "diploma"
    assert data[0]["hash_verificacion"] is not None


@pytest.mark.asyncio
async def test_list_documentos_filter_alumno(client: AsyncClient, auth_headers, seed_documento):
    response = await client.get(
        "/api/v1/documentos?cod_alumno=ALU001", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get(
        "/api/v1/documentos?cod_alumno=ALU999", headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_list_documentos_requires_auth(client: AsyncClient):
    response = await client.get("/api/v1/documentos")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_documentos_pagination(client: AsyncClient, auth_headers, seed_alumno, db_session):
    """Test pagination on document listing."""
    for i in range(5):
        hash_verificacion = f"{i:064x}"
        doc = DocumentoGenerado(
            tipo=TipoDocumento.diploma,
            cod_alumno="ALU001",
            hash_verificacion=hash_verificacion,
            qr_data=f"qr_{i}.png",
            archivo_path=f"generated/doc_{i}.docx",
        )
        db_session.add(doc)
    await db_session.commit()

    response = await client.get("/api/v1/documentos?skip=0&limit=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = await client.get("/api/v1/documentos?skip=3&limit=10", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


# ── Generar Documento ────────────────────────────────────────


@pytest.mark.asyncio
async def test_generar_documento_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/documentos/generar",
        json={"plantilla_id": 1, "cod_alumno": "ALU001"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_generar_documento_docente_forbidden(client: AsyncClient, docente_headers):
    response = await client.post(
        "/api/v1/documentos/generar",
        headers=docente_headers,
        json={"plantilla_id": 1, "cod_alumno": "ALU001"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_generar_documento_alumno_not_found(
    client: AsyncClient, auth_headers, seed_plantilla
):
    """Generation with non-existent alumno returns 404."""
    response = await client.post(
        "/api/v1/documentos/generar",
        headers=auth_headers,
        json={"plantilla_id": seed_plantilla.id, "cod_alumno": "NOEXIST"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_generar_documento_plantilla_not_found(
    client: AsyncClient, auth_headers, seed_alumno
):
    """Generation with non-existent plantilla returns 404."""
    response = await client.post(
        "/api/v1/documentos/generar",
        headers=auth_headers,
        json={"plantilla_id": 99999, "cod_alumno": "ALU001"},
    )
    assert response.status_code == 404


# ── Generar Masivo ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_generar_masivo_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/v1/documentos/generar/masivo?plantilla_id=1&cod_alumnos=ALU001"
    )
    assert response.status_code in (401, 403)


# ── Analizar ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analizar_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/documentos/analizar")
    assert response.status_code in (401, 403)
