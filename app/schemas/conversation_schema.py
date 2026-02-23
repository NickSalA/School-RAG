"""Esquemas de Pydantic para la gestión de conversaciones."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ConversationBase(BaseModel):
    content: list[dict] = Field(..., description="Lista de mensajes en la conversación, cada mensaje es un diccionario con claves como 'role' y 'content'.")
    prompt_id: int = Field(..., description="ID del prompt asociado a esta conversación.")

class ConversationCreate(ConversationBase):
    pass

class ConversationRead(ConversationBase):
    id: int = Field(..., description="ID único de la conversación.")
    created_at: datetime = Field(..., description="Fecha y hora de creación de la conversación.")

    model_config = ConfigDict(from_attributes=True)
