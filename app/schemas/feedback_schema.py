"""Esquemas de Pydantic para la gestión de feedbacks."""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class FeedbackBase(BaseModel):
    task_resolved: bool = Field(..., description="Indica si la tarea fue resuelta o no.")
    rating: int | None = Field(default=None, ge=1, le=5, description="Calificación del 1 al 5 para la tarea.")
    comments: str | None = Field(default=None, description="Comentarios adicionales sobre la tarea.")

class FeedbackCreate(FeedbackBase):
    conversation_id: int = Field(..., description="ID de la conversación a la que se refiere este feedback.")

class FeedbackRead(FeedbackBase):
    id: int = Field(..., description="ID único del feedback.")
    conversation_id: int = Field(..., description="ID de la conversación a la que se refiere este feedback.")
    created_at: datetime = Field(..., description="Fecha y hora de creación del feedback.")

    model_config = ConfigDict(from_attributes=True)
