"""Esquemas de Pydantic para la gestión de conversaciones."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ConversationBase(BaseModel):
    content: list[dict] = Field(..., description="Lista de mensajes en la conversación, cada mensaje es un diccionario con claves como 'role' y 'content'.")
    prompt_id: int | None = Field(default=None, description="ID del prompt asociado a esta conversación.")

class ConversationCreate(ConversationBase):
    user_id: int = Field(..., description="ID del usuario propietario de la conversación.")

class ConversationUpdate(BaseModel):
    content: list[dict] | None = None
    prompt_id: int | None = None

class ConversationRead(ConversationBase):
    id: int = Field(..., description="ID único de la conversación.")
    user_id: int = Field(..., description="ID del usuario propietario de la conversación.")
    created_at: datetime = Field(..., description="Fecha y hora de creación de la conversación.")

    model_config = ConfigDict(from_attributes=True)

class ConversationList(BaseModel):
    id: int = Field(..., description="ID único de la conversación.")
    user_id: int = Field(..., description="ID del usuario propietario de la conversación.")
    prompt_id: int | None = Field(default=None, description="ID del prompt asociado a esta conversación.")
    created_at: datetime = Field(..., description="Fecha y hora de creación de la conversación.")

    model_config = ConfigDict(from_attributes=True)
