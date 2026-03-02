"""Esquemas de Pydantic para la gestión de logs."""

from typing import Any, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models import ResourceType

class LogBase(BaseModel):
    user_id: int = Field(..., description="ID del usuario al que se refiere este log.")
    action: str = Field(..., description="Descripción de la acción realizada por el usuario.")
    resource_type: ResourceType = Field(..., description="Tipo de recurso afectado por la acción.")
    resource_id: str = Field(..., description="ID del recurso afectado por la acción.")
    details: Dict[str, Any] = Field(default=..., description="Detalles adicionales sobre la acción realizada.")

class LogCreate(LogBase):
    pass

class LogRead(LogBase):
    id: int = Field(..., description="ID único del log.")
    created_at: datetime = Field(..., description="Fecha y hora en que se registró el log.")

    model_config = ConfigDict(from_attributes=True)
