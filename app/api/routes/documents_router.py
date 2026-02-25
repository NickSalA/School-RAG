"""Router para el agente de flujo."""

from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Depends
from pypdf import PdfReader
from qdrant_client import AsyncQdrantClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.config import settings

from app.schemas.documents_schema import DocumentJSON, ResponseJSON
from app.services.document_service import DocumentService
from app.adapters.qdrant import connect_async_vectorial_client

from app.api.dependencies.dep_auth import get_current_user

from app.exceptions.cloud import DocumentFormatError, DocumentSizeError, DocumentQualityError


router = APIRouter()

@router.post("/upload", response_model=ResponseJSON)
async def upload(file: Annotated[UploadFile, File(description="Archivo a subir")],
                session: AsyncSession = Depends(get_session),
                current_user = Depends(get_current_user),
                client: AsyncQdrantClient = Depends(connect_async_vectorial_client)):
    """Endpoint para subir un archivo."""

    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise DocumentFormatError(f"Tipo de archivo no permitido: {file.content_type}")

    if settings.MAX_FILE_SIZE:
        max_bytes: int = settings.MAX_FILE_SIZE * 1024 * 1024
        if file.size is not None and file.size > max_bytes:
            raise DocumentSizeError(f"Archivo demasiado grande. Máximo permitido: {settings.MAX_FILE_SIZE} MB")

    if settings.MAX_NUM_PAGES and file.content_type == "application/pdf":
        try:
            reader = PdfReader(file.file)
            num_pages = len(reader.pages)
            file.file.seek(0)
            if num_pages > settings.MAX_NUM_PAGES:
                raise DocumentSizeError(f"El PDF tiene {num_pages} páginas, excediendo el límite de {settings.MAX_NUM_PAGES}.")
        except Exception as e:
            raise DocumentQualityError(f"Error al leer el archivo PDF: {e}") from e

    service = DocumentService(session, client)
    await service.upload_document(file, user_id=current_user.id)
    return ResponseJSON(message=f"Archivo {file.filename} subido y procesado exitosamente.")

@router.get("/",response_model=DocumentJSON)
async def get_documents(client: AsyncQdrantClient = Depends(connect_async_vectorial_client)):
    """Endpoint para obtener los documentos subidos."""
    service = DocumentService(None, client)
    documents = await service.get_uploaded_documents()
    return DocumentJSON(message="Documentos obtenidos exitosamente.", documents=documents)

@router.delete("/", response_model=ResponseJSON)
async def delete_documents(filename: str,
                        session: AsyncSession = Depends(get_session),
                        current_user = Depends(get_current_user),
                        client: AsyncQdrantClient = Depends(connect_async_vectorial_client)):
    """Endpoint para eliminar un documento subido."""
    service = DocumentService(session, client)

    if not filename or not filename.strip():
        raise DocumentFormatError("El nombre del archivo no puede estar vacío.")
    documents = await service.get_uploaded_documents()
    if filename not in documents:
        raise DocumentFormatError(f"El archivo '{filename}' no existe en los documentos subidos.")

    await service.delete_document(filename=filename, user_id=current_user.id)
    return ResponseJSON(message=f"Documento '{filename}' eliminado exitosamente.")
