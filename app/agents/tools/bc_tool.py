"""Tool de base de conocimientos para el agente."""

# Manejo de herramientas y agentes
from langchain_core.tools import Tool

# Helpers propios
from app.services.retriever import get_retriever

# Utilitario para crear tool de base de conocimientos
from app.util.retriever_tool import create_retriever_tool

def bc_tool(index: str) -> Tool:
    """Crear una herramienta de base de conocimientos para el agente.
    
    Args:
        index: Nombre de la colección/índice en Qdrant a consultar.
    
    Returns:
        Tool: Herramienta de LangChain configurada para búsqueda en la base de conocimientos.
    """
    return create_retriever_tool(
        retriever=get_retriever(index),
        name="bc_tool",
        description="""Úsala para buscar información en reglamentos, normativas y documentos oficiales de la universidad.
        Devuelve fragmentos relevantes de la base de conocimientos institucional."""
    )
