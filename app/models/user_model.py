"""Modelo de base de datos para usuarios."""

from enum import Enum

from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy import Column, Integer, String
class Role(str, Enum):
    ADMIN = "ADMIN"
    SUPERADMIN = "SUPERADMIN"
class User(SQLModel, table=True):
    """Modelo SQLAlchemy para los usuarios del sistema."""
    __tablename__: str = "user"
    __table_args__ = {"schema": "school_rag"}

    id: int = Field(default=None, sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column("name", String, nullable=False))
    email: str = Field(sa_column=Column("email", String, nullable=False, unique=True))
    password: str = Field(sa_column=Column("password", String, nullable=False))
    role: Role = Field(sa_column=Column("role", PgEnum(Role, name="role", schema="school_rag"), nullable=False))
