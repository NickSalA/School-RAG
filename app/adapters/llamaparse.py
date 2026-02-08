"""Analizador de documentos usando LlamaParse."""

from llama_parse import LlamaParse, ResultType
from app.core.config import settings
from app.exceptions.cloud import DocumentAIError

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
