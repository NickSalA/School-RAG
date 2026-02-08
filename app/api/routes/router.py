"""Router para el agente de flujo."""

from fastapi import APIRouter, Depends

from app.api.schema import AgentMessageJson, ChatIn
from app.agents.flow import FlowAgent
from app.api.dependencies import get_flow_agent
from app.exceptions.cloud import AgentResponseError

router = APIRouter()


@router.post("/chat", response_model=AgentMessageJson)
async def agente(body: ChatIn, orq: FlowAgent = Depends(get_flow_agent)):
    """Endpoint para interactuar con el agente de flujo."""
    thread = body.thread_id

    if not thread:
        thread = orq.generate_thread_id()

    try:
        respuesta = await orq.answer_message(body.mensaje, thread)
    except Exception as e:
        raise AgentResponseError(f"Error al procesar mensaje: {e}") from e

    return AgentMessageJson(text=respuesta, thread_id=thread)
