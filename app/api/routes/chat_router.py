"""Router para el agente de flujo."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from sqlmodel.ext.asyncio.session import AsyncSession

# Schemas
from app.schemas import AgentMessageJson, ChatIn

from app.models import User

# Database
from app.core.database import get_session

# Services
from app.services.chat_service import ChatService

# Flow Agent to control the flow of the conversation
from app.agents.flow import FlowAgent

# Dependency to get the flow agent
from app.api.dependencies.dep_auth import get_current_user

router = APIRouter()

async def get_flow_agent(request: Request) -> FlowAgent:
    """Dependencia para obtener una instancia del FlowAgent."""
    return request.app.state.flow_agent

FlowAgentDep = Annotated[FlowAgent, Depends(get_flow_agent)]
UserDep = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/chat", response_model=AgentMessageJson)
async def agente(body: ChatIn, orq: FlowAgentDep, session: SessionDep, current_user: UserDep):
    """Endpoint para interactuar con el agente de flujo."""
    service = ChatService(session, orq)

    response, conversation_id = await service.chat(body, current_user)
    return AgentMessageJson(text=response, conversation_id=conversation_id)
