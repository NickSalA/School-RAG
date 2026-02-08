"""Dependencias de FastAPI para inyección en endpoints.

Este módulo define singletons y factories para evitar
recrear objetos costosos en cada request.
"""

from functools import lru_cache

from app.agents.flow import FlowAgent


@lru_cache(maxsize=1)
def get_flow_agent() -> FlowAgent:
    """Singleton del FlowAgent.
    
    Usa lru_cache para garantizar que solo se crea una instancia
    durante todo el ciclo de vida de la aplicación.
    
    Returns:
        FlowAgent: Instancia compartida del agente.
    """
    return FlowAgent()
