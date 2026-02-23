"""Manejo de excepciones relacionadas con servicios en la nube externos."""

from app.exceptions.base import AppError

class ExternalServiceError(AppError):
    """Error al interactuar con un servicio externo."""
    status_code = 502


# Secretos

class AzureAuthError(ExternalServiceError):
    """Error de autenticación con Azure Key Vault."""
    status_code = 503
class SecretError(ExternalServiceError):
    """Error genérico relacionado con la gestión de secretos."""
    status_code = 502

class SecretNotFoundError(SecretError):
    """Error cuando un secreto no es encontrado."""
    status_code = 404

class SecretEmptyError(SecretError):
    """Error cuando un secreto obtenido está vacío."""
    status_code = 404

# Document AI
class DocumentAIError(ExternalServiceError):
    """Error al interactuar con Google Document AI."""
    status_code = 502

class DocumentFormatError(DocumentAIError):
    """El archivo enviado no tiene un formato soportado (ej. no es PDF/Imagen)."""
    status_code = 415

class DocumentSizeError(DocumentAIError):
    """El documento excede el tamaño máximo permitido por Google (bytes o páginas)."""
    status_code = 413

class DocumentQualityError(DocumentAIError):
    """El OCR no pudo procesar el archivo por baja resolución o estar corrupto."""
    status_code = 422

class DocumentTimeoutError(DocumentAIError):
    """La solicitud a Google tardó demasiado en procesarse."""
    status_code = 504

# Generative AI

class GenerativeAIError(ExternalServiceError):
    """Error al interactuar con Google Generative AI."""
    status_code = 502

class GenerativeAIQuotaError(GenerativeAIError):
    """Se ha excedido la cuota asignada para el uso del modelo generativo."""
    status_code = 429

class GenerativeAITimeoutError(GenerativeAIError):
    """La solicitud al modelo generativo tardó demasiado en procesarse."""
    status_code = 504

class GenerativeAIContentError(GenerativeAIError):
    """El contenido generado por el modelo no es adecuado o está bloqueado."""
    status_code = 422

class GenerativeAIModelError(GenerativeAIError):
    """Error interno relacionado con el modelo generativo."""
    status_code = 500

class AgentExecutionError(GenerativeAIError):
    """Error durante la ejecución del agente conversacional."""
    status_code = 500


class AgentNotAvailableError(GenerativeAIError):
    """El agente no está disponible o no pudo inicializarse."""
    status_code = 503


class AgentResponseError(GenerativeAIError):
    """Error al procesar la respuesta del agente."""
    status_code = 500

# Auth
class AuthError(AppError):
    """Excepción base para errores de autenticación."""
    status_code = 401

class InvalidTokenError(AuthError):
    """El token de autenticación proporcionado es inválido."""
    status_code = 401
