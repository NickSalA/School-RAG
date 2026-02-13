"""Esquema de mensajes del agente en formato JSON."""

from typing import Optional
from google.protobuf import message
from pydantic import BaseModel, Field

class AgentMessageJson(BaseModel):
    text: str
    thread_id: str

class ChatIn(BaseModel):
    mensaje: str = Field (default="string", description="El mensaje del usuario al agente.")
    thread_id: Optional[str] = Field (default=None, description="El ID único de la conversación. Enviar 'null' o 'None' si es el primer mensaje.")

class ResponseJSON(BaseModel):
    message: str = Field(default="string", description="Mensaje de respuesta al subir el documento.")

class DocumentJSON(BaseModel):
    message: Optional[str] = Field(default=None, description="Mensaje de respuesta al obtener los documentos subidos.")
    documents: Optional[list[str]] = Field(default_factory=list, description="Lista de documentos subidos a la colección.")
