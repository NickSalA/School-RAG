"""Utilitario para persistencia del estado del agente."""
from langgraph.checkpoint.memory import MemorySaver

saver = MemorySaver()

def get_checkpointer() -> MemorySaver:
    """Obtener el checkpointer para persistencia del estado.
    
    Returns:
        MemorySaver: Instancia del checkpointer en memoria.
    """
    return saver
