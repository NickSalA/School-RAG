"""Dependencias para el módulo de chat."""

from fastapi import Request

# Flow Agent to control the flow of the conversation
from app.agents.flow import FlowAgent

async def get_flow_agent(request: Request) -> FlowAgent:
    """Dependencia para obtener una instancia del FlowAgent."""
    return request.app.state.flow_agent
