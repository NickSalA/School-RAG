"""Utilitario para el modelo de lenguaje"""
from langchain_google_genai import ChatGoogleGenerativeAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import Settings

# Helpers propios
from app.core.config import settings


def get_llm() -> ChatGoogleGenerativeAI:
    """ Obtener el LLM de Google Generative AI.
    Returns:
        ChatGoogleGenerativeAI: Instancia del modelo de lenguaje.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        api_key=settings.MODEL_API_KEY,
        temperature = settings.MODEL_TEMPERATURE,
    )

def configure_embedding():
    """Configura el modelo de embedding Google GenAI para su uso en el proyecto."""
    Settings.embed_model = GoogleGenAIEmbedding(
        model_name=settings.GEMINI_EMBEDDING_MODEL_NAME,
        api_key=settings.MODEL_API_KEY,
    )
