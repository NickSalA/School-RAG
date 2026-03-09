"""Esquema de mensajes del agente en formato JSON."""

from typing import Optional
from pydantic import BaseModel, Field

class AgentMessageJson(BaseModel):
    text: str
    conversation_id: Optional[int] = None

class ChatIn(BaseModel):
    message: str = Field (default="string", description="El mensaje del usuario al agente.")
    conversation_id: Optional[int] = Field (default=None, description="El ID de la conversación en la base de datos. Enviar 'null' o 'None' si es el primer mensaje.")
