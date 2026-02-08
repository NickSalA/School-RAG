"""Adaptador para Google Generative AI (Gemini)."""

from langchain_google_genai import ChatGoogleGenerativeAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings

from app.core.config import settings
from app.exceptions.cloud import GenerativeAIModelError

def get_llm() -> ChatGoogleGenerativeAI:
    """Obtener el LLM de Google Generative AI.
    
    Returns:
        ChatGoogleGenerativeAI: Instancia del modelo de lenguaje.
    
    Raises:
        GenerativeAIModelError: Si hay error al inicializar el modelo.
    """
    try:
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=settings.MODEL_API_KEY,
            temperature=settings.MODEL_TEMPERATURE,
        )
    except Exception as e:
        raise GenerativeAIModelError(
            f"Error al inicializar el modelo Gemini: {e}"
        ) from e


def configure_embedding() -> None:
    """Configura el modelo de embedding Google GenAI para LlamaIndex.
    
    Raises:
        GenerativeAIError: Si hay error al configurar embeddings.
    """
    try:
        Settings.embed_model = GoogleGenAIEmbedding(
            model_name=settings.GEMINI_EMBEDDING_MODEL_NAME,
            api_key=settings.MODEL_API_KEY,
        )
    except Exception as e:
        raise GenerativeAIModelError(f"Error al configurar modelo de embeddings: {e}") from e
