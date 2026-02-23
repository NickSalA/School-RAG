"""Esquemas de Pydantic para la gestión de prompts."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class PromptStructure(BaseModel):
    identity: str = Field(..., description="Identidad del agente o sistema para el que se genera el prompt.")
    rules: str = Field(..., description="Reglas específicas para el prompt.")
    workflow: str = Field(..., description="Flujo de trabajo o pasos a seguir para el prompt.")
    communication_style: str = Field(..., description="Estilo de comunicación a utilizar en el prompt.")

    model_config = ConfigDict(extra="allow")

class PromptBase(BaseModel):
    version_name: str = Field(..., description="Nombre de la versión del prompt.")
    system_message: PromptStructure = Field(..., description="Estructura del mensaje del sistema.")

class PromptCreate(PromptBase):
    is_active: bool = Field(default=True, description="Indica si esta versión del prompt está activa.")

class PromptRead(PromptBase):
    id: int = Field(..., description="ID único del prompt.")
    is_active: bool = Field(..., description="Indica si esta versión del prompt está activa.")
    created_at: datetime = Field(..., description="Fecha y hora de creación del prompt.")

    model_config = ConfigDict(from_attributes=True)

class PromptUpdate(BaseModel):
    version_name: str | None = None
    system_message: PromptStructure | None = None
    is_active: bool | None = None
