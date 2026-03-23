"""Legacy CRUD smoke tests — see test_cursos.py, test_notas.py, test_alumnos.py for full coverage."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crud_requires_auth(client: AsyncClient):
    """All CRUD endpoints should return 401 without token."""
    endpoints = [
        ("GET", "/api/v1/alumnos"),
        ("GET", "/api/v1/docentes"),
        ("GET", "/api/v1/tutores"),
        ("GET", "/api/v1/cursos"),
        ("GET", "/api/v1/materias"),
        ("GET", "/api/v1/notas"),
        ("GET", "/api/v1/periodos"),
    ]
    for method, url in endpoints:
        response = await client.request(method, url)
        assert response.status_code == 401, f"{method} {url} should require auth"
