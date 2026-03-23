"""Shared API dependencies: database session, current user, role checks."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.database import get_db
from app.models.usuario import UserRole, Usuario

security_scheme = HTTPBearer(auto_error=False)

DB = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DB,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
) -> Usuario:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")

    payload = decode_token(credentials.credentials)
    if payload is None or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")

    result = await db.execute(select(Usuario).where(Usuario.id == int(user_id)))
    user = result.scalar_one_or_none()
    if user is None or not user.activo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


CurrentUser = Annotated[Usuario, Depends(get_current_user)]


def require_roles(*roles: UserRole):
    """Dependency factory that enforces the user has one of the given roles."""

    async def _check(user: CurrentUser) -> Usuario:
        if user.rol not in roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Role '{user.rol.value}' not authorized. Required: {[r.value for r in roles]}",
            )
        return user

    return Depends(_check)


AdminUser = Annotated[Usuario, require_roles(UserRole.admin)]
AdminOrSecretaria = Annotated[Usuario, require_roles(UserRole.admin, UserRole.secretaria)]
