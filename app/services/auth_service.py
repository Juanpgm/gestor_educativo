"""Authentication service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.usuario import Usuario
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


async def register_user(db: AsyncSession, data: RegisterRequest) -> Usuario:
    """Create a new user. Raises ValueError if email already exists."""
    result = await db.execute(select(Usuario).where(Usuario.email == data.email))
    if result.scalar_one_or_none() is not None:
        raise ValueError("Email already registered")

    user = Usuario(
        email=data.email,
        password_hash=hash_password(data.password),
        nombre=data.nombre,
        apellidos=data.apellidos,
        rol=data.rol,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    """Validate credentials and return JWT tokens. Raises ValueError on failure."""
    result = await db.execute(select(Usuario).where(Usuario.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        raise ValueError("Invalid email or password")
    if not user.activo:
        raise ValueError("Account is inactive")

    token_data = {"sub": str(user.id), "email": user.email, "rol": user.rol.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Issue new tokens from a valid refresh token."""
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise ValueError("Invalid refresh token")

    user_id = payload.get("sub")
    result = await db.execute(select(Usuario).where(Usuario.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.activo:
        raise ValueError("User not found or inactive")

    token_data = {"sub": str(user.id), "email": user.email, "rol": user.rol.value}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
