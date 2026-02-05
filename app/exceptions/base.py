"""Módulo base de excepciones personalizadas para la aplicación."""

class AppError(Exception):
    """Clase base para errores de la aplicación."""
    status_code = 400

    def __init__(self, message: str = "Error interno de la aplicación"):
        super().__init__(message)
        self.message = message
