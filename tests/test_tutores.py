"""Tests for Tutores CRUD endpoints."""

import pytest
from httpx import AsyncClient

TUTOR_DATA = {
    "cod_tutor": "TUT001",
    "identificacion": "5555555555",
    "nombre": "Carlos",
    "apellidos": "Martínez",
    "parentesco": "padre",
    "fecha_nacimiento": "1975-08-10",
    "email": "carlos@example.com",
    "telefono": "3205555555",
    "direccion": "Carrera 50 #30-40",
}


@pytest.mark.asyncio
async def test_list_tutores_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/tutores", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_tutor(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/tutores", headers=auth_headers, json=TUTOR_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_tutor"] == "TUT001"
    assert data["nombre"] == "Carlos"
    assert data["parentesco"] == "padre"
    assert data["identificacion"] == "5555555555"
    assert data["email"] == "carlos@example.com"


@pytest.mark.asyncio
async def test_create_tutor_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/tutores", json=TUTOR_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_tutor_docente_forbidden(client: AsyncClient, docente_headers):
    response = await client.post("/api/v1/tutores", headers=docente_headers, json=TUTOR_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_tutor(client: AsyncClient, auth_headers):
    await client.post("/api/v1/tutores", headers=auth_headers, json=TUTOR_DATA)

    response = await client.get("/api/v1/tutores/TUT001", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["cod_tutor"] == "TUT001"


@pytest.mark.asyncio
async def test_get_tutor_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/tutores/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_tutor(client: AsyncClient, auth_headers):
    await client.post("/api/v1/tutores", headers=auth_headers, json=TUTOR_DATA)

    response = await client.put(
        "/api/v1/tutores/TUT001",
        headers=auth_headers,
        json={"nombre": "Carlos Andrés", "parentesco": "padrastro"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Carlos Andrés"
    assert data["parentesco"] == "padrastro"
    assert data["apellidos"] == "Martínez"


@pytest.mark.asyncio
async def test_update_tutor_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/tutores/NOEXIST",
        headers=auth_headers,
        json={"nombre": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tutor(client: AsyncClient, auth_headers):
    await client.post("/api/v1/tutores", headers=auth_headers, json=TUTOR_DATA)

    response = await client.delete("/api/v1/tutores/TUT001", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get("/api/v1/tutores/TUT001", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_tutor_not_found(client: AsyncClient, auth_headers):
    response = await client.delete("/api/v1/tutores/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_tutor_list_pagination(client: AsyncClient, auth_headers):
    for i in range(4):
        t = {**TUTOR_DATA, "cod_tutor": f"TUT{i:03d}", "identificacion": f"TID{i:06d}"}
        await client.post("/api/v1/tutores", headers=auth_headers, json=t)

    response = await client.get("/api/v1/tutores?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/api/v1/tutores?skip=2&limit=10", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_tutor_pii_encrypted(client: AsyncClient, auth_headers, db_session):
    await client.post("/api/v1/tutores", headers=auth_headers, json=TUTOR_DATA)

    from sqlalchemy import select
    from app.models.tutor import Tutor

    result = await db_session.execute(select(Tutor).where(Tutor.cod_tutor == "TUT001"))
    tutor = result.scalar_one()
    assert tutor.identificacion != "5555555555"
    assert tutor.email != "carlos@example.com"


@pytest.mark.asyncio
async def test_tutor_update_pii_encrypts(client: AsyncClient, auth_headers, db_session):
    """Updated PII fields should be re-encrypted."""
    await client.post("/api/v1/tutores", headers=auth_headers, json=TUTOR_DATA)
    await client.put(
        "/api/v1/tutores/TUT001",
        headers=auth_headers,
        json={"email": "newemail@example.com"},
    )

    response = await client.get("/api/v1/tutores/TUT001", headers=auth_headers)
    assert response.json()["email"] == "newemail@example.com"

    from sqlalchemy import select
    from app.models.tutor import Tutor

    db_session.expire_all()
    result = await db_session.execute(select(Tutor).where(Tutor.cod_tutor == "TUT001"))
    tutor = result.scalar_one()
    assert tutor.email != "newemail@example.com"
