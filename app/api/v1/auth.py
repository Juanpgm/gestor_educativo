"""Auth API endpoints: login, register, refresh."""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import AdminUser, CurrentUser, DB
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import authenticate_user, refresh_tokens, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(db: DB, data: LoginRequest):
    try:
        return await authenticate_user(db, data)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(db: DB, data: RegisterRequest, admin: AdminUser):
    """Only admins can register new users."""
    try:
        user = await register_user(db, data)
        return user
    except ValueError as e:
        raise HTTPException(status.HTTP_409_CONFLICT, str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(db: DB, data: RefreshRequest):
    try:
        return await refresh_tokens(db, data.refresh_token)
    except ValueError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e))


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser):
    return user
