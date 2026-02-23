"""Modelo de base de datos para las auditorias."""

from typing import Any
from enum import Enum
from datetime import datetime, timezone

from sqlmodel import ForeignKey, SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB, ENUM as PgEnum
from sqlalchemy import Column, Integer, DateTime, String

class ResourceType(str, Enum):
    QDRANT_COLLECTION = "QDRANT_COLLECTION"
    SYSTEM_PROMPT = "SYSTEM_PROMPT"

class Log(SQLModel, table=True):
    """Modelo SQLAlchemy para los registros de auditoría."""
    __tablename__: str = "audit_log"
    __table_args__ = {"schema": "school_rag"}

    id: int = Field(default=None, sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    user_id: int = Field(sa_column=Column("user_id", Integer, ForeignKey("school_rag.user.id"), nullable=False))
    action: str = Field(sa_column=Column("action", String, nullable=False))
    resource_type: ResourceType = Field(sa_column=Column("resource_type", PgEnum(ResourceType, name="resource_type", schema="school_rag"), nullable=False))
    resource_id: str = Field(sa_column=Column("resource_id", String))
    details: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column("details", JSONB))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column("created_at", DateTime(timezone=True), nullable=False))
