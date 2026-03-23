"""Shared schema utilities: pagination, common fields."""

from pydantic import BaseModel


class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 50


class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list
