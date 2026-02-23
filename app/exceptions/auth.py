"""Manejo de excepciones relacionadas con autenticación."""

from app.exceptions.base import AppError

class AuthenticationError(AppError):
    """Error de autenticación general."""
    status_code = 401

class InvalidCredentialsError(AuthenticationError):
    """Credenciales de usuario inválidas."""
    status_code = 401

class UserNotFoundError(AuthenticationError):
    """Usuario no encontrado en la base de datos."""
    status_code = 404

class TokenGenerationError(AuthenticationError):
    """Error al generar el token de autenticación."""
    status_code = 500

class TokenValidationError(AuthenticationError):
    """Error al validar el token de autenticación."""
    status_code = 401

class PermissionDeniedError(AuthenticationError):
    """El usuario no tiene permisos para acceder al recurso."""
    status_code = 403
