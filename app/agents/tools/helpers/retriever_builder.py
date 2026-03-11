"""Servicio para obtener un retriever de LlamaIndex configurado con un índice específico."""

from llama_index.core import VectorStoreIndex

from app.adapters.qdrant import get_async_vector_store, connect_async_vectorial_client
from app.agents.tools.helpers.retriever_bridge import LlamaIndexWindowRetriever
from app.exceptions.database import VectorStoreQueryError
from loguru import logger


async def get_retriever(collection_name: str) -> LlamaIndexWindowRetriever:
    """Obtener un retriever de LlamaIndex configurado con el índice dado.
    
    Args:
        collection_name: Nombre de la colección a usar para el retriever.
    
    Returns:
        LlamaIndexWindowRetriever: Instancia del retriever configurado.
    
    Raises:
        VectorStoreQueryError: Si hay error al crear el retriever.
        VectorStoreConnectionError: Si no se puede conectar a Qdrant.
        VectorStoreCollectionNotFoundError: Si la colección no existe.
    """
    try:
        logger.debug("[Retriever] Conectando a Qdrant...")
        client = await connect_async_vectorial_client()
        logger.debug("[Retriever] Obteniendo vector store...")
        vector_store = await get_async_vector_store(client, collection_name)
        logger.debug("[Retriever] Creando índice VectorStoreIndex...")
        index = VectorStoreIndex.from_vector_store(vector_store)
        logger.debug("[Retriever] Retriever listo.")
        return LlamaIndexWindowRetriever(index=index, top_k=5)
    except Exception as e:
        # Re-raise si ya es una excepción personalizada
        if hasattr(e, 'status_code'):
            raise
        raise VectorStoreQueryError(
            f"Error al crear retriever para '{collection_name}': {e}") from e
