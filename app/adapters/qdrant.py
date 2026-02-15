"""Servicios de almacenamiento vectorial (Qdrant)."""

from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore

from app.core.config import settings
from app.exceptions.database import (
    VectorStoreConnectionError,
    VectorStoreCollectionNotFoundError,
)


def connect_vectorial_client() -> QdrantClient:
    """Conectar al cliente de Qdrant.
    
    Returns:
        QdrantClient: Instancia del cliente de Qdrant.
    
    Raises:
        VectorStoreConnectionError: Si no se puede conectar al servidor.
    """
    try:
        client = QdrantClient(
            api_key=settings.QDRANR_API_KEY,
            url=settings.QDRANT_URL
        )
        # Verificar conexión
        client.get_collections()
        return client
    except Exception as e:
        raise VectorStoreConnectionError(
            f"No se pudo conectar a Qdrant: {e}") from e


def get_vector_store(client: QdrantClient, index_name: str) -> QdrantVectorStore:
    """Obtener el vector store de Qdrant.
    
    Args:
        client: Cliente de Qdrant conectado.
        index_name: Nombre de la colección en Qdrant.
    
    Returns:
        QdrantVectorStore: Instancia del vector store.
    
    Raises:
        VectorStoreCollectionNotFoundError: Si la colección no existe.
    """
    try:
        # Verificar que la colección existe
        if not client.collection_exists(index_name):
            raise VectorStoreCollectionNotFoundError(
                f"La colección '{index_name}' no existe en Qdrant."
            )

        return QdrantVectorStore(
            client=client,
            collection_name=index_name
        )
    except VectorStoreCollectionNotFoundError:
        raise
    except Exception as e:
        raise VectorStoreConnectionError(f"Error al obtener vector store '{index_name}': {e}") from e
