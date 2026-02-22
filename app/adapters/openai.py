"""Adaptador para OpenAI."""

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
            model_name="text-embedding-3-small",
            api_key=settings.OPENAI_API,
            embed_batch_size=50,
            dimensions=768,
        )
    except Exception as e:
        raise GenerativeAIModelError(f"Error al configurar modelo de embeddings OpenAI: {e}") from e
