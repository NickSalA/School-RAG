"""Servicio para obtener un retriever de LlamaIndex configurado con un índice específico."""

from llama_index.core import VectorStoreIndex

from app.adapters.qdrant import get_vector_store, connect_vectorial_client
from app.util.retriever import LlamaIndexWindowRetriever

def get_retriever(collection_name: str):
    """Obtener un retriever de LlamaIndex configurado con el índice dado.
    Args:
        collection_name (str): Nombre del índice a usar para el retriever.
    Returns:
        LlamaIndexWindowRetriever: Instancia del retriever configurado.
    """
    vector_store = get_vector_store(connect_vectorial_client(), collection_name)
    index = VectorStoreIndex.from_vector_store(vector_store)
    retriever = LlamaIndexWindowRetriever(index=index, top_k=3)
    return retriever
