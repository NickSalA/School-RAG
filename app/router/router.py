"""Router para el agente de flujo."""

from fastapi import APIRouter, HTTPException

from app.core.schema import AgentMessageJson, ChatIn
from app.flow.flow import FlowAgent

router = APIRouter()

@router.post("/chat", response_model=AgentMessageJson)
async def agente(body: ChatIn):
    """Endpoint para interactuar con el agente de flujo."""
    orq = FlowAgent()
    thread = body.thread_id

    if not thread:
        thread = orq.reset_memory()
    try:
        respuesta = await orq.answer_message(body.mensaje, thread)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error al enviar el mensaje: {e}') from e

    return AgentMessageJson(text=respuesta, thread_id=thread)
