"""Modelo de base de datos para la retroalimentación."""

from datetime import datetime, timezone

from sqlmodel import ForeignKey, SQLModel, Field
from sqlalchemy import Column, Integer, DateTime, Boolean, String

class Feedback(SQLModel, table=True):
    """Modelo SQLAlchemy para la retroalimentación."""
    __tablename__: str = "chat_feedback"
    __table_args__ = {"schema": "school_rag"}

    id: int = Field(default=None, sa_column=Column("id", Integer, primary_key=True, autoincrement=True))
    conversation_id: int = Field(sa_column=Column("conversation_id", Integer, ForeignKey("school_rag.chat_conversation.id"), unique=True, nullable=False))
    task_resolved: bool = Field(sa_column=Column("task_resolved", Boolean, nullable=False))
    rating: int = Field(sa_column=Column("rating", Integer))
    comments: str = Field(sa_column=Column("comments", String))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column("created_at", DateTime(timezone=True), nullable=False))
