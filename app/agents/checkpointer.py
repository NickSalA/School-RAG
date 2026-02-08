"""Gestión del estado/memoria de conversaciones del agente.

Nota: MemorySaver almacena en RAM y NO persiste entre reinicios.
Para producción, considerar usar PostgresSaver o RedisSaver.
"""
from langgraph.checkpoint.memory import MemorySaver

saver = MemorySaver()

def get_checkpointer() -> MemorySaver:
    """Obtener el checkpointer singleton para el estado de conversaciones.
    
    Warning:
        Esta implementación usa memoria volátil. Los datos se pierden
        al reiniciar la aplicación o entre workers distintos.
    
    Returns:
        MemorySaver: Instancia compartida del checkpointer en memoria.
    """
    return saver
