"""Adaptador para integrar el modelo de lenguaje de Groq en la aplicación."""

from langchain_groq import ChatGroq

from app.core.config import settings

from app.exceptions.cloud import GenerativeAIModelError

def get_secondary_llm() -> ChatGroq:
    """Obtener el LLM de Groq.
    
    Returns:
        ChatGroq: Instancia del modelo de lenguaje.
    
    Raises:
        GenerativeAIModelError: Si hay error al inicializar el modelo.
    """
    try:
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.MODEL_SECOND_API_KEY,
            temperature=settings.MODEL_TEMPERATURE,
        )
    except Exception as e:
        raise GenerativeAIModelError(
            f"Error al inicializar el modelo Groq: {e}"
        ) from e
