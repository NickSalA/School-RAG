"""Modelo de base de datos para las conversaciones."""
from typing import Any
from datetime import datetime, timezone

from sqlmodel import ForeignKey, SQLModel, Field
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, DateTime

class Conversation(SQLModel, table=True):
    """Modelo SQLAlchemy para las conversaciones."""
    __tablename__: str = "chat_conversation"
    __table_args__ = {"schema": "school_rag"}

    id: int = Field(default=None, sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    user_id: int = Field(default=None, sa_column=Column("user_id", Integer, ForeignKey("school_rag.user.id"), nullable=False))
    prompt_id: int = Field(default=None, sa_column=Column("prompt_id", Integer, ForeignKey("school_rag.system_prompt.id"),nullable=False))
    content: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column("content", JSONB, nullable=False))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column("created_at", DateTime(timezone=True), nullable=False))
