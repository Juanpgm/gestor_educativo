"""Tests for Cursos CRUD endpoints."""

import pytest
from httpx import AsyncClient

CURSO_DATA = {
    "cod_curso": "CUR001",
    "nombre_curso": "Matemáticas 10",
    "descripcion": "Curso de matemáticas grado 10",
    "grado": "10",
    "activo": True,
}


@pytest.mark.asyncio
async def test_list_cursos_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/cursos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_curso(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_curso"] == "CUR001"
    assert data["nombre_curso"] == "Matemáticas 10"
    assert data["grado"] == "10"
    assert data["activo"] is True
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_curso_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/cursos", json=CURSO_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_curso_docente_forbidden(client: AsyncClient, docente_headers):
    response = await client.post("/api/v1/cursos", headers=docente_headers, json=CURSO_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_curso(client: AsyncClient, auth_headers):
    await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)

    response = await client.get("/api/v1/cursos/CUR001", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["cod_curso"] == "CUR001"


@pytest.mark.asyncio
async def test_get_curso_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/cursos/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_cursos_filter_grado(client: AsyncClient, auth_headers):
    await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)
    curso2 = {**CURSO_DATA, "cod_curso": "CUR002", "nombre_curso": "Ciencias 11", "grado": "11"}
    await client.post("/api/v1/cursos", headers=auth_headers, json=curso2)

    response = await client.get("/api/v1/cursos?grado=10", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["grado"] == "10"


@pytest.mark.asyncio
async def test_list_cursos_filter_activo(client: AsyncClient, auth_headers):
    await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)
    curso2 = {**CURSO_DATA, "cod_curso": "CUR002", "activo": False}
    await client.post("/api/v1/cursos", headers=auth_headers, json=curso2)

    response = await client.get("/api/v1/cursos?activo=true", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["activo"] is True


@pytest.mark.asyncio
async def test_list_cursos_pagination(client: AsyncClient, auth_headers):
    for i in range(5):
        c = {**CURSO_DATA, "cod_curso": f"CUR{i:03d}"}
        await client.post("/api/v1/cursos", headers=auth_headers, json=c)

    response = await client.get("/api/v1/cursos?skip=0&limit=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3


@pytest.mark.asyncio
async def test_update_curso(client: AsyncClient, auth_headers):
    await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)

    response = await client.put(
        "/api/v1/cursos/CUR001",
        headers=auth_headers,
        json={"nombre_curso": "Matemáticas Avanzadas", "activo": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre_curso"] == "Matemáticas Avanzadas"
    assert data["activo"] is False
    assert data["grado"] == "10"


@pytest.mark.asyncio
async def test_update_curso_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/cursos/NOEXIST",
        headers=auth_headers,
        json={"nombre_curso": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_curso(client: AsyncClient, auth_headers):
    await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)

    response = await client.delete("/api/v1/cursos/CUR001", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get("/api/v1/cursos/CUR001", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_curso_not_found(client: AsyncClient, auth_headers):
    response = await client.delete("/api/v1/cursos/NOEXIST", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_and_list_cursos_full_flow(client: AsyncClient, auth_headers):
    """Full CRUD flow: create → list → update → verify → delete."""
    # Create
    resp = await client.post("/api/v1/cursos", headers=auth_headers, json=CURSO_DATA)
    assert resp.status_code == 201

    # List
    resp = await client.get("/api/v1/cursos", headers=auth_headers)
    assert len(resp.json()) == 1

    # Update
    resp = await client.put(
        "/api/v1/cursos/CUR001",
        headers=auth_headers,
        json={"descripcion": "Updated description"},
    )
    assert resp.status_code == 200
    assert resp.json()["descripcion"] == "Updated description"

    # Delete
    resp = await client.delete("/api/v1/cursos/CUR001", headers=auth_headers)
    assert resp.status_code == 204

    # Verify deleted
    resp = await client.get("/api/v1/cursos", headers=auth_headers)
    assert resp.json() == []
