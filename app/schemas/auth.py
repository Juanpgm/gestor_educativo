"""Auth schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.models.usuario import UserRole


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    nombre: str = Field(..., max_length=100)
    apellidos: str = Field(..., max_length=100)
    rol: UserRole = UserRole.docente


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    nombre: str
    apellidos: str
    rol: UserRole
    activo: bool

    model_config = {"from_attributes": True}
