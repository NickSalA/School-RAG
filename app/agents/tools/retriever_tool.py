"""Tool de base de conocimientos para el agente."""

# Manejo de herramientas y agentes
from langchain_core.tools import Tool

# Helpers propios
from app.agents.tools.helpers.retriever_builder import get_retriever

# Utilitario para crear tool de base de conocimientos
from app.agents.tools.helpers.custom_retriever_factory import create_retriever_tool


async def bc_tool(index: str) -> Tool:
    """Crear una herramienta de base de conocimientos para el agente.
    
    Args:
        index: Nombre de la colección/índice en Qdrant a consultar.
    
    Returns:
        Tool: Herramienta de LangChain configurada para búsqueda en la base de conocimientos.
    """
    retriever = await get_retriever(index)
    return create_retriever_tool(
        retriever=retriever,
        name="bc_tool",
        description="""Úsala para buscar información en reglamentos, normativas y documentos oficiales de la universidad.
        Devuelve fragmentos relevantes de la base de conocimientos institucional."""
    )
