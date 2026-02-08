"""Módulo base de excepciones personalizadas para la aplicación."""


class AppError(Exception):
    """Clase base para errores de la aplicación.
    
    Todas las excepciones personalizadas deben heredar de esta clase
    para ser capturadas por el exception handler global en factory.py.
    
    Attributes:
        status_code: Código HTTP a retornar (default: 400).
        message: Mensaje descriptivo del error.
    """
    status_code = 400

    def __init__(self, message: str = "Error interno de la aplicación"):
        super().__init__(message)
        self.message = message

# Errores de validación/cliente.

class ValidationError(AppError):
    """Error de validación de datos de entrada."""
    status_code = 400

class NotFoundError(AppError):
    """Recurso no encontrado."""
    status_code = 404

class ConflictError(AppError):
    """Conflicto con el estado actual del recurso."""
    status_code = 409
