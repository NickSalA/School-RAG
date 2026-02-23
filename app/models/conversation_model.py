"""Modelo de base de datos para las conversaciones."""

from datetime import datetime, timezone

from sqlmodel import ForeignKey, SQLModel, Field
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, DateTime

class Conversation(SQLModel, table=True):
    """Modelo SQLAlchemy para las conversaciones."""
    __tablename__: str = "chat_conversation"

    id: int = Field(default=None, sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    prompt_id: int = Field(sa_column=Column("prompt_id", Integer, ForeignKey("system_prompt.id"),nullable=False))
    content: Mapped[dict] = mapped_column("content", JSONB, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column("created_at", DateTime(timezone=True), nullable=False))
