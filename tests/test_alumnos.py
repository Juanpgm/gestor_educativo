"""Tests for Alumnos CRUD endpoints."""

import pytest
from httpx import AsyncClient

ALUMNO_DATA = {
    "cod_alumno": "ALU001",
    "identificacion": "1234567890",
    "nombre": "Juan",
    "apellidos": "Pérez García",
    "grado": "10",
    "fecha_nacimiento": "2008-05-15",
    "fecha_ingreso": "2023-01-15",
    "email": "juan@example.com",
    "telefono": "3001234567",
    "direccion": "Calle 123 #45-67",
}


@pytest.mark.asyncio
async def test_list_alumnos_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/alumnos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_alumno(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_alumno"] == "ALU001"
    assert data["nombre"] == "Juan"
    assert data["apellidos"] == "Pérez García"
    assert data["grado"] == "10"
    # PII should be decrypted in response
    assert data["identificacion"] == "1234567890"
    assert data["email"] == "juan@example.com"
    assert data["telefono"] == "3001234567"
    assert data["direccion"] == "Calle 123 #45-67"
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_alumno_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/alumnos", json=ALUMNO_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_alumno_docente_forbidden(client: AsyncClient, docente_headers):
    """Docentes cannot create alumnos, only admin/secretaria."""
    response = await client.post("/api/v1/alumnos", headers=docente_headers, json=ALUMNO_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_alumno_secretaria_allowed(client: AsyncClient, secretaria_headers):
    response = await client.post("/api/v1/alumnos", headers=secretaria_headers, json=ALUMNO_DATA)
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_alumno(client: AsyncClient, auth_headers):
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    response = await client.get("/api/v1/alumnos/ALU001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["cod_alumno"] == "ALU001"
    assert data["nombre"] == "Juan"
    assert data["identificacion"] == "1234567890"


@pytest.mark.asyncio
async def test_get_alumno_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/alumnos/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_alumnos_after_create(client: AsyncClient, auth_headers):
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    response = await client.get("/api/v1/alumnos", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["cod_alumno"] == "ALU001"


@pytest.mark.asyncio
async def test_list_alumnos_filter_by_grado(client: AsyncClient, auth_headers):
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    alumno2 = {**ALUMNO_DATA, "cod_alumno": "ALU002", "identificacion": "9999999999", "grado": "11"}
    await client.post("/api/v1/alumnos", headers=auth_headers, json=alumno2)

    response = await client.get("/api/v1/alumnos?grado=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["grado"] == "10"


@pytest.mark.asyncio
async def test_list_alumnos_pagination(client: AsyncClient, auth_headers):
    for i in range(5):
        a = {**ALUMNO_DATA, "cod_alumno": f"ALU{i:03d}", "identificacion": f"ID{i:06d}"}
        await client.post("/api/v1/alumnos", headers=auth_headers, json=a)

    response = await client.get("/api/v1/alumnos?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = await client.get("/api/v1/alumnos?skip=3&limit=10", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_update_alumno(client: AsyncClient, auth_headers):
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    response = await client.put(
        "/api/v1/alumnos/ALU001",
        headers=auth_headers,
        json={"nombre": "Juan Carlos", "grado": "11"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Juan Carlos"
    assert data["grado"] == "11"
    # Unchanged fields intact
    assert data["apellidos"] == "Pérez García"


@pytest.mark.asyncio
async def test_update_alumno_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/alumnos/NOEXIST",
        headers=auth_headers,
        json={"nombre": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_alumno(client: AsyncClient, auth_headers):
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    response = await client.delete("/api/v1/alumnos/ALU001", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get("/api/v1/alumnos/ALU001", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_alumno_not_found(client: AsyncClient, auth_headers):
    response = await client.delete("/api/v1/alumnos/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_alumno_pii_encryption(client: AsyncClient, auth_headers, db_session):
    """Verify PII is stored encrypted in DB but returned decrypted via API."""
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    from sqlalchemy import select
    from app.models.alumno import Alumno

    result = await db_session.execute(select(Alumno).where(Alumno.cod_alumno == "ALU001"))
    alumno = result.scalar_one()
    # DB value should be encrypted (not the plain text)
    assert alumno.identificacion != "1234567890"
    assert alumno.email != "juan@example.com"
    assert alumno.telefono != "3001234567"

    # API response should decrypt
    response = await client.get("/api/v1/alumnos/ALU001", headers=auth_headers)
    data = response.json()
    assert data["identificacion"] == "1234567890"
    assert data["email"] == "juan@example.com"


@pytest.mark.asyncio
async def test_alumno_antiguedad_calculated(client: AsyncClient, auth_headers):
    """antiguedad_dias should be calculated from fecha_ingreso."""
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    response = await client.get("/api/v1/alumnos/ALU001", headers=auth_headers)
    data = response.json()
    assert data["antiguedad_dias"] is not None
    assert isinstance(data["antiguedad_dias"], int)
    assert data["antiguedad_dias"] >= 0


@pytest.mark.asyncio
async def test_alumno_docente_can_read(client: AsyncClient, auth_headers, docente_headers):
    """Docentes can list/read alumnos but not create/update/delete."""
    await client.post("/api/v1/alumnos", headers=auth_headers, json=ALUMNO_DATA)

    response = await client.get("/api/v1/alumnos", headers=docente_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/v1/alumnos/ALU001", headers=docente_headers)
    assert response.status_code == 200
