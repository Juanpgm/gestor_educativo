"""Tests for Notas and Periodos endpoints."""

from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.core.security import hash_password
from app.models.alumno import Alumno
from app.models.materia import Materia
from app.models.periodo import PeriodoAcademico
from app.utils.encryption import encrypt_value

PERIODO_DATA = {
    "cod_periodo": "2024-1",
    "nombre": "Primer Semestre 2024",
    "anio": 2024,
    "fecha_inicio": "2024-01-15T00:00:00",
    "fecha_fin": "2024-06-30T00:00:00",
    "activo": True,
}


@pytest_asyncio.fixture
async def seed_nota_deps(db_session):
    """Seed prerequisite data for notas: alumno, materia, periodo."""
    alumno = Alumno(
        cod_alumno="ALU001",
        identificacion=encrypt_value("1234567890"),
        nombre="Juan",
        apellidos="Pérez",
        grado="10",
        fecha_nacimiento=date(2008, 5, 15),
        fecha_ingreso=date(2023, 1, 15),
    )
    materia = Materia(
        cod_materia="MAT001",
        nombre_materia="Matemáticas",
    )
    periodo = PeriodoAcademico(
        cod_periodo="2024-1",
        nombre="Primer Semestre 2024",
        anio=2024,
        fecha_inicio=date(2024, 1, 15),
        fecha_fin=date(2024, 6, 30),
    )
    db_session.add_all([alumno, materia, periodo])
    await db_session.commit()
    return {"alumno": alumno, "materia": materia, "periodo": periodo}


# ── Periodos ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_periodos_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/periodos", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_periodo(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/periodos", headers=auth_headers, json=PERIODO_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_periodo"] == "2024-1"
    assert data["nombre"] == "Primer Semestre 2024"
    assert data["anio"] == 2024
    assert data["activo"] is True


@pytest.mark.asyncio
async def test_create_periodo_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/periodos", json=PERIODO_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_periodo_docente_forbidden(client: AsyncClient, docente_headers):
    response = await client.post("/api/v1/periodos", headers=docente_headers, json=PERIODO_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_periodo(client: AsyncClient, auth_headers):
    await client.post("/api/v1/periodos", headers=auth_headers, json=PERIODO_DATA)

    response = await client.put(
        "/api/v1/periodos/2024-1",
        headers=auth_headers,
        json={"nombre": "Updated Periodo", "activo": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Updated Periodo"
    assert data["activo"] is False


@pytest.mark.asyncio
async def test_update_periodo_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/periodos/NOEXIST",
        headers=auth_headers,
        json={"nombre": "Test"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_periodos_filter_activo(client: AsyncClient, auth_headers):
    await client.post("/api/v1/periodos", headers=auth_headers, json=PERIODO_DATA)
    p2 = {**PERIODO_DATA, "cod_periodo": "2024-2", "nombre": "Segundo", "activo": False}
    await client.post("/api/v1/periodos", headers=auth_headers, json=p2)

    response = await client.get("/api/v1/periodos?activo=true", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


# ── Notas ────────────────────────────────────────────────────


import pytest_asyncio


NOTA_DATA = {
    "cod_alumno": "ALU001",
    "cod_materia": "MAT001",
    "cod_periodo": "2024-1",
    "nota": 8.50,
}


@pytest.mark.asyncio
async def test_list_notas_empty(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/notas", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_nota(client: AsyncClient, auth_headers, seed_nota_deps):
    response = await client.post("/api/v1/notas", headers=auth_headers, json=NOTA_DATA)
    assert response.status_code == 201
    data = response.json()
    assert data["cod_alumno"] == "ALU001"
    assert data["cod_materia"] == "MAT001"
    assert data["cod_periodo"] == "2024-1"
    assert data["nota"] == 8.50
    assert data["nombre_alumno"] == "Juan Pérez"
    assert data["nombre_materia"] == "Matemáticas"
    assert data["nombre_periodo"] == "Primer Semestre 2024"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_nota_requires_auth(client: AsyncClient):
    response = await client.post("/api/v1/notas", json=NOTA_DATA)
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_nota_docente_forbidden(client: AsyncClient, docente_headers, seed_nota_deps):
    response = await client.post("/api/v1/notas", headers=docente_headers, json=NOTA_DATA)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_nota_invalid_grade(client: AsyncClient, auth_headers, seed_nota_deps):
    """Grade value must be between 0 and 10."""
    nota_invalid = {**NOTA_DATA, "nota": 11.0}
    response = await client.post("/api/v1/notas", headers=auth_headers, json=nota_invalid)
    assert response.status_code == 422

    nota_negative = {**NOTA_DATA, "nota": -1.0}
    response = await client.post("/api/v1/notas", headers=auth_headers, json=nota_negative)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_nota(client: AsyncClient, auth_headers, seed_nota_deps):
    resp = await client.post("/api/v1/notas", headers=auth_headers, json=NOTA_DATA)
    nota_id = resp.json()["id"]

    response = await client.get(f"/api/v1/notas/{nota_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["nota"] == 8.50


@pytest.mark.asyncio
async def test_get_nota_not_found(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/notas/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_nota(client: AsyncClient, auth_headers, seed_nota_deps):
    resp = await client.post("/api/v1/notas", headers=auth_headers, json=NOTA_DATA)
    nota_id = resp.json()["id"]

    response = await client.put(
        f"/api/v1/notas/{nota_id}",
        headers=auth_headers,
        json={"nota": 9.25},
    )
    assert response.status_code == 200
    assert response.json()["nota"] == 9.25


@pytest.mark.asyncio
async def test_update_nota_not_found(client: AsyncClient, auth_headers):
    response = await client.put(
        "/api/v1/notas/99999",
        headers=auth_headers,
        json={"nota": 5.0},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nota(client: AsyncClient, auth_headers, seed_nota_deps):
    resp = await client.post("/api/v1/notas", headers=auth_headers, json=NOTA_DATA)
    nota_id = resp.json()["id"]

    response = await client.delete(f"/api/v1/notas/{nota_id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/notas/{nota_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nota_not_found(client: AsyncClient, auth_headers):
    response = await client.delete("/api/v1/notas/99999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_notas_filter_alumno(client: AsyncClient, auth_headers, seed_nota_deps):
    await client.post("/api/v1/notas", headers=auth_headers, json=NOTA_DATA)

    response = await client.get("/api/v1/notas?cod_alumno=ALU001", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = await client.get("/api/v1/notas?cod_alumno=ALU999", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_list_notas_filter_periodo(client: AsyncClient, auth_headers, seed_nota_deps):
    await client.post("/api/v1/notas", headers=auth_headers, json=NOTA_DATA)

    response = await client.get("/api/v1/notas?cod_periodo=2024-1", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_bulk_create_notas(client: AsyncClient, auth_headers, seed_nota_deps, db_session):
    """Test bulk creation of notas."""
    # Add a second materia
    materia2 = Materia(cod_materia="FIS001", nombre_materia="Física")
    db_session.add(materia2)
    await db_session.commit()

    bulk_data = {
        "notas": [
            {"cod_alumno": "ALU001", "cod_materia": "MAT001", "cod_periodo": "2024-1", "nota": 8.0},
            {"cod_alumno": "ALU001", "cod_materia": "FIS001", "cod_periodo": "2024-1", "nota": 7.5},
        ]
    }
    response = await client.post("/api/v1/notas/bulk", headers=auth_headers, json=bulk_data)
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2
    assert data[0]["nota"] == 8.0
    assert data[1]["nota"] == 7.5


@pytest.mark.asyncio
async def test_notas_pagination(client: AsyncClient, auth_headers, seed_nota_deps, db_session):
    """Test nota pagination with skip/limit."""
    # Create multiple materias for multiple notas
    for i in range(5):
        m = Materia(cod_materia=f"SUB{i:03d}", nombre_materia=f"Subject {i}")
        db_session.add(m)
    await db_session.commit()

    for i in range(5):
        nota = {
            "cod_alumno": "ALU001",
            "cod_materia": f"SUB{i:03d}",
            "cod_periodo": "2024-1",
            "nota": float(5 + i),
        }
        await client.post("/api/v1/notas", headers=auth_headers, json=nota)

    response = await client.get("/api/v1/notas?skip=0&limit=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = await client.get("/api/v1/notas?skip=3&limit=10", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
