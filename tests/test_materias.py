"""Tests for Materias CRUD endpoints."""

import pytest
from httpx import AsyncClient

MATERIA_DATA = {
    "cod_materia": "MAT001",
    "nombre_materia": "Matemáticas",
    "descripcion": "Álgebra y geometría",
    "activo": True,
    "grados": ["10", "11"],
}


@pytest.mark.asyncio
async def test_list_materias_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/materias", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_materia(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_materia"] == "MAT001"
    assert data["nombre_materia"] == "Matemáticas"
    assert data["activo"] is True
    assert set(data["grados"]) == {"10", "11"}
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_materia_no_grados(client: AsyncClient, auth_headers):
    materia = {**MATERIA_DATA, "cod_materia": "MAT002", "grados": []}
    response = await client.post("/api/v1/materias", headers=auth_headers, json=materia)
    assert response.status_code == 201
    assert response.json()["grados"] == []


@pytest.mark.asyncio
async def test_create_materia_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/materias", json=MATERIA_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_materia_docente_forbidden(client: AsyncClient, docente_headers):
    response = await client.post("/api/v1/materias", headers=docente_headers, json=MATERIA_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_materia(client: AsyncClient, auth_headers):
    await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)

    response = await client.get("/api/v1/materias/MAT001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["cod_materia"] == "MAT001"
    assert set(data["grados"]) == {"10", "11"}


@pytest.mark.asyncio
async def test_get_materia_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/materias/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_materias_filter_activo(client: AsyncClient, auth_headers):
    await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)
    m2 = {**MATERIA_DATA, "cod_materia": "MAT002", "activo": False, "grados": []}
    await client.post("/api/v1/materias", headers=auth_headers, json=m2)

    response = await client.get("/api/v1/materias?activo=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["activo"] is True


@pytest.mark.asyncio
async def test_update_materia(client: AsyncClient, auth_headers):
    await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)

    response = await client.put(
        "/api/v1/materias/MAT001",
        headers=auth_headers,
        json={"nombre_materia": "Matemáticas Avanzadas", "grados": ["11", "12"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre_materia"] == "Matemáticas Avanzadas"
    assert set(data["grados"]) == {"11", "12"}


@pytest.mark.asyncio
async def test_update_materia_partial(client: AsyncClient, auth_headers):
    """Partial update should only change specified fields."""
    await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)

    response = await client.put(
        "/api/v1/materias/MAT001",
        headers=auth_headers,
        json={"descripcion": "New description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["descripcion"] == "New description"
    assert data["nombre_materia"] == "Matemáticas"


@pytest.mark.asyncio
async def test_update_materia_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/materias/NOEXIST",
        headers=auth_headers,
        json={"nombre_materia": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_materia(client: AsyncClient, auth_headers):
    await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)

    response = await client.delete("/api/v1/materias/MAT001", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get("/api/v1/materias/MAT001", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_materia_not_found(client: AsyncClient, auth_headers):
    response = await client.delete("/api/v1/materias/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_materia_pagination(client: AsyncClient, auth_headers):
    for i in range(4):
        m = {**MATERIA_DATA, "cod_materia": f"MAT{i:03d}", "grados": []}
        await client.post("/api/v1/materias", headers=auth_headers, json=m)

    response = await client.get("/api/v1/materias?skip=0&limit=2", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_materia_grados_many_to_many(client: AsyncClient, auth_headers):
    """Create materia with grados, update grados, verify association persists."""
    await client.post("/api/v1/materias", headers=auth_headers, json=MATERIA_DATA)

    # Verify initial grados
    resp = await client.get("/api/v1/materias/MAT001", headers=auth_headers)
    assert set(resp.json()["grados"]) == {"10", "11"}

    # Update grados
    await client.put(
        "/api/v1/materias/MAT001",
        headers=auth_headers,
        json={"grados": ["9", "10", "11", "12"]},
    )
    resp = await client.get("/api/v1/materias/MAT001", headers=auth_headers)
    assert set(resp.json()["grados"]) == {"9", "10", "11", "12"}

    # Clear grados
    await client.put(
        "/api/v1/materias/MAT001",
        headers=auth_headers,
        json={"grados": []},
    )
    resp = await client.get("/api/v1/materias/MAT001", headers=auth_headers)
    assert resp.json()["grados"] == []
