"""Esquema de mensajes del agente en formato JSON."""

from typing import Optional
from pydantic import BaseModel, Field

class AgentMessageJson(BaseModel):
    text: str
    thread_id: str

class ChatIn(BaseModel):
    mensaje: str = Field (default="string", description="El mensaje del usuario al agente.")
    thread_id: Optional[str] = Field (default=None, description="El ID único de la conversación. Enviar 'null' o 'None' si es el primer mensaje.")
