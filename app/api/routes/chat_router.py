"""Router para el agente de flujo."""

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.chat_schema import AgentMessageJson, ChatIn
from app.agents.flow import FlowAgent
from app.api.dependencies.dep_chat import get_flow_agent
from app.core.database import get_session
from app.services.chat import ChatService

router = APIRouter()

FlowAgentDep = Annotated[FlowAgent, Depends(get_flow_agent)]

@router.post("/chat", response_model=AgentMessageJson)
async def agente(body: ChatIn, orq: FlowAgentDep, session: AsyncSession = Depends(get_session)):
    """Endpoint para interactuar con el agente de flujo."""
    service = ChatService(session, orq)

    response, conversation_id, thread_id = await service.chat(body.mensaje, body.thread_id, body.conversation_id)
    return AgentMessageJson(text=response, thread_id=thread_id, conversation_id=conversation_id)
