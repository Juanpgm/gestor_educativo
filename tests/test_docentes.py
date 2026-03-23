"""Tests for Docentes CRUD endpoints."""

import pytest
from httpx import AsyncClient

DOCENTE_DATA = {
    "cod_docente": "DOC001",
    "identificacion": "9876543210",
    "nombre": "María",
    "apellidos": "López Rodríguez",
    "fecha_nacimiento": "1985-03-20",
    "fecha_ingreso": "2020-02-01",
    "email": "maria@example.com",
    "telefono": "3109876543",
    "direccion": "Av. Principal #10-20",
}


@pytest.mark.asyncio
async def test_list_docentes_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/docentes", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_docente(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_docente"] == "DOC001"
    assert data["nombre"] == "María"
    assert data["apellidos"] == "López Rodríguez"
    assert data["identificacion"] == "9876543210"
    assert data["email"] == "maria@example.com"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_docente_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/docentes", json=DOCENTE_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_docente_docente_forbidden(client: AsyncClient, docente_headers):
    response = await client.post("/api/v1/docentes", headers=docente_headers, json=DOCENTE_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_docente(client: AsyncClient, auth_headers):
    await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)

    response = await client.get("/api/v1/docentes/DOC001", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["cod_docente"] == "DOC001"


@pytest.mark.asyncio
async def test_get_docente_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/docentes/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_docentes_pagination(client: AsyncClient, auth_headers):
    for i in range(3):
        d = {**DOCENTE_DATA, "cod_docente": f"DOC{i:03d}", "identificacion": f"DID{i:06d}"}
        await client.post("/api/v1/docentes", headers=auth_headers, json=d)

    response = await client.get("/api/v1/docentes?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_docente(client: AsyncClient, auth_headers):
    await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)

    response = await client.put(
        "/api/v1/docentes/DOC001",
        headers=auth_headers,
        json={"nombre": "María Elena", "email": "mariaelena@example.com"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "María Elena"
    assert data["email"] == "mariaelena@example.com"
    assert data["apellidos"] == "López Rodríguez"


@pytest.mark.asyncio
async def test_update_docente_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/docentes/NOEXIST",
        headers=auth_headers,
        json={"nombre": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_docente(client: AsyncClient, auth_headers):
    await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)

    response = await client.delete("/api/v1/docentes/DOC001", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get("/api/v1/docentes/DOC001", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_docente_not_found(client: AsyncClient, auth_headers):
    response = await client.delete("/api/v1/docentes/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_docente_pii_encrypted_in_db(client: AsyncClient, auth_headers, db_session):
    """PII fields must be encrypted at rest."""
    await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)

    from sqlalchemy import select
    from app.models.docente import Docente

    result = await db_session.execute(select(Docente).where(Docente.cod_docente == "DOC001"))
    docente = result.scalar_one()
    assert docente.identificacion != "9876543210"
    assert docente.email != "maria@example.com"
    assert docente.telefono != "3109876543"


@pytest.mark.asyncio
async def test_docente_antiguedad(client: AsyncClient, auth_headers):
    await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)

    response = await client.get("/api/v1/docentes/DOC001", headers=auth_headers)
    data = response.json()
    assert data["antiguedad_dias"] is not None
    assert data["antiguedad_dias"] >= 0


@pytest.mark.asyncio
async def test_docente_can_read_list(client: AsyncClient, auth_headers, docente_headers):
    """Docentes can read the list of docentes."""
    await client.post("/api/v1/docentes", headers=auth_headers, json=DOCENTE_DATA)

    response = await client.get("/api/v1/docentes", headers=docente_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
