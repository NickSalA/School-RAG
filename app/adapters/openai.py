"""Adaptador para OpenAI."""

from pydantic import SecretStr

from langchain_openai import OpenAIEmbeddings

from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.core import Settings

from app.core.config import settings

from app.exceptions.cloud import GenerativeAIModelError

def configure_embedding() -> None:
    """Configura el modelo de embedding OpenAI para LlamaIndex.
    
    Raises:
        GenerativeAIError: Si hay error al configurar embeddings.
    """
    try:
        Settings.embed_model = OpenAIEmbedding(
            model_name=settings.OPENAI_EMBEDDING_MODEL_NAME,
            api_key=settings.OPENAI_API,
            embed_batch_size=50,
            dimensions=768,
        )
    except Exception as e:
        raise GenerativeAIModelError(f"Error al configurar modelo de embeddings OpenAI: {e}") from e

def get_embedding() -> OpenAIEmbeddings:
    """Obtiene una instancia de OpenAIEmbeddings.
    
    Returns:
        OpenAIEmbeddings: Instancia del modelo de embeddings.
    
    Raises:
        GenerativeAIModelError: Si hay error al inicializar el modelo de embeddings.
    """
    try:
        return OpenAIEmbeddings(
            model=settings.OPENAI_EMBEDDING_MODEL_NAME,
            api_key=SecretStr(settings.OPENAI_API)
        )
    except Exception as e:
        raise GenerativeAIModelError(f"Error al inicializar modelo de embeddings OpenAI: {e}") from e
