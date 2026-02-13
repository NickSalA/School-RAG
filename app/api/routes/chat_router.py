"""Router para el agente de flujo."""

from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.schema import AgentMessageJson, ChatIn
from app.agents.flow import FlowAgent
from app.api.dependencies import get_flow_agent
from app.exceptions.cloud import AgentResponseError

router = APIRouter()

FlowAgentDep = Annotated[FlowAgent, Depends(get_flow_agent)]

@router.post("/chat", response_model=AgentMessageJson)
async def agente(body: ChatIn, orq: FlowAgentDep):
    """Endpoint para interactuar con el agente de flujo."""
    thread = body.thread_id

    if not thread:
        thread = orq.generate_thread_id()

    respuesta = await orq.answer_message(body.mensaje, thread)
    return AgentMessageJson(text=respuesta, thread_id=thread)
