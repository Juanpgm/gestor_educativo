"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.com", "password": "wrongpassword1"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_short_password_rejected(client: AsyncClient):
    """Password must be at least 8 characters per schema validation."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "short"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["rol"] == "admin"
    assert data["nombre"] == "Admin"
    assert data["apellidos"] == "Test"
    assert data["activo"] is True


@pytest.mark.asyncio
async def test_get_me_no_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_requires_admin(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@test.com",
            "password": "NewPass123!",
            "nombre": "New",
            "apellidos": "User",
            "rol": "docente",
        },
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_register_docente_cannot_register(client: AsyncClient, docente_headers):
    """Docentes cannot register new users, only admins."""
    response = await client.post(
        "/api/v1/auth/register",
        headers=docente_headers,
        json={
            "email": "another@test.com",
            "password": "AnotherPass1!",
            "nombre": "Another",
            "apellidos": "User",
            "rol": "docente",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/auth/register",
        headers=auth_headers,
        json={
            "email": "teacher@test.com",
            "password": "TeacherPass1!",
            "nombre": "Teacher",
            "apellidos": "Test",
            "rol": "docente",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "teacher@test.com"
    assert data["rol"] == "docente"
    assert data["activo"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, auth_headers, admin_user):
    """Registering with an existing email returns 409."""
    response = await client.post(
        "/api/v1/auth/register",
        headers=auth_headers,
        json={
            "email": "admin@test.com",
            "password": "DuplicatePass1!",
            "nombre": "Dup",
            "apellidos": "User",
            "rol": "docente",
        },
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_secretaria(client: AsyncClient, auth_headers):
    response = await client.post(
        "/api/v1/auth/register",
        headers=auth_headers,
        json={
            "email": "sec@test.com",
            "password": "SecretariaP1!",
            "nombre": "Sec",
            "apellidos": "Test",
            "rol": "secretaria",
        },
    )
    assert response.status_code == 201
    assert response.json()["rol"] == "secretaria"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, admin_user):
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    refresh_token = login_resp.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_with_access_token_fails(client: AsyncClient, admin_user):
    """Using an access token as a refresh should fail."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    access_token = login_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_then_access_me(client: AsyncClient, admin_user):
    """Full flow: login → use token → access /me."""
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "AdminPass123!"},
    )
    token = login_resp.json()["access_token"]

    me_resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "admin@test.com"
