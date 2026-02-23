"""Modelo de base de datos para usuarios."""

from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID, uuid4

class User(SQLModel, table=True):
    """Modelo SQLAlchemy para los usuarios del sistema."""
    __tablename__: str = "users" # type: ignore

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    role: str = Field(default="admin", nullable=False)
