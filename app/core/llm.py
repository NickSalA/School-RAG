"""Utilitario para el modelo de lenguaje"""
from langchain_google_genai import ChatGoogleGenerativeAI

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
