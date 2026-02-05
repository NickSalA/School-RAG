"""Cliente de Azure Cognitive Search."""

from llama_parse import LlamaParse, ResultType
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore
# Helpers propios
from app.core.config import settings
from app.exceptions.cloud import DocumentAIError

def connect_vectorial_client():
    """ Conectar al cliente de Qdrant.
    Returns:
        QdrantClient: Instancia del cliente de Qdrant.
    """
    client = QdrantClient(
        port=settings.QDRANT_PORT,
        url=settings.QDRANT_HOST
    )
    return client

def get_vector_store(client: QdrantClient, index_name: str):
    """ Obtener el vector store de Qdrant.
    Args:
        index_name (str): Nombre del índice en Qdrant.
    Returns:
        QdrantVectorStore: Instancia del vector store.
    """
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=index_name
    )
    return vector_store

def get_analyzer() -> LlamaParse:
    """ Conectar al cliente de LlamaParse.
    Returns:
        LlamaParse: Instancia del cliente de análisis de documentos.
    """
    try:
        parser = LlamaParse(
            api_key=settings.LLAMA_PARSE_API_KEY,
            result_type =ResultType.MD,
            verbose=False
            )
        return parser
    except Exception as e:
        raise DocumentAIError(f"Error al conectar con LlamaParse: {e}") from e
