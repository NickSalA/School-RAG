"""Modelo de base de datos para los prompts."""

from typing import Any
from datetime import datetime, timezone

from sqlmodel import SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, Boolean, DateTime

class Prompt(SQLModel, table=True):
    """Modelo SQLAlchemy para los prompts."""
    __tablename__: str = "system_prompt"
    __table_args__ = {"schema": "school_rag"}

    id: int = Field(default=None, sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    version_name: str = Field(sa_column=Column("version_name", String, nullable=False, unique=True))
    system_message: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column("system_message", JSONB))
    is_active: bool = Field(sa_column=Column("is_active", Boolean))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column("created_at", DateTime(timezone=True), nullable=False))
