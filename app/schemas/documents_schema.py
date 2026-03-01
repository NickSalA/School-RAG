"""Schemas para la API de documentos."""

from typing import Optional
from pydantic import BaseModel, Field

class ResponseJSON(BaseModel):
    message: str = Field(default="string", description="Mensaje de respuesta al subir el documento.")

class DocumentJSON(BaseModel):
    message: Optional[str] = Field(default=None, description="Mensaje de respuesta al obtener los documentos subidos.")
    documents: Optional[list[str]] = Field(default_factory=list, description="Lista de documentos subidos a la colección.")
