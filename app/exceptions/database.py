"""Excepciones relacionadas con bases de datos y almacenamiento vectorial."""

from app.exceptions.base import AppError


# Errores de Vector Store (Qdrant)
class VectorStoreError(AppError):
    """Error base para operaciones con el vector store."""
    status_code = 502


class VectorStoreConnectionError(VectorStoreError):
    """No se pudo conectar al servidor de vector store (Qdrant)."""
    status_code = 503


class VectorStoreCollectionNotFoundError(VectorStoreError):
    """La colección/índice solicitado no existe en el vector store."""
    status_code = 404


class VectorStoreQueryError(VectorStoreError):
    """Error al ejecutar una consulta en el vector store."""
    status_code = 500


class VectorStoreIndexError(VectorStoreError):
    """Error al crear o actualizar un índice en el vector store."""
    status_code = 500
