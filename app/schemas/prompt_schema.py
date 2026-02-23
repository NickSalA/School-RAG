"""Esquemas de Pydantic para la gestión de prompts."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class PromptStructure(BaseModel):
    section: str = Field(..., description="Sección del prompt, por ejemplo: 'identity_objectives', 'critical_rules', etc.")
    content: str = Field(..., description="Contenido específico de la sección del prompt.")

class PromptBase(BaseModel):
    version_name: str = Field(..., description="Nombre de la versión del prompt.")
    system_message: PromptStructure = Field(..., description="Estructura del mensaje del sistema.")
    is_active: bool = Field(default=True, description="Indica si esta versión del prompt está activa.")

class PromptCreate(PromptBase):
    pass

class PromptRead(PromptBase):
    id: int = Field(..., description="ID único del prompt.")
    created_at: datetime = Field(..., description="Fecha y hora de creación del prompt.")

    model_config = ConfigDict(from_attributes=True)

class PromptUpdate(BaseModel):
    version_name: str | None = None
    is_active: bool | None = None
