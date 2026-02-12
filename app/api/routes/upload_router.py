"""Router para el agente de flujo."""

from typing import Annotated
from fastapi import APIRouter, UploadFile, File
from pypdf import PdfReader
from app.services.documents import upload_file
from app.core.config import settings

from app.api.schema import DocumentJSON

from app.exceptions.cloud import DocumentAIError
from app.exceptions.cloud import DocumentFormatError, DocumentSizeError, DocumentQualityError

router = APIRouter()

@router.post("/upload", response_model=DocumentJSON)
def upload(file: Annotated[UploadFile, File(description="Archivo a subir")]):
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
    try :
        upload_file(file, index=settings.INDEX_NAME)
        return DocumentJSON(message="Archivo subido y procesado exitosamente.")
    except Exception as e:
        raise DocumentAIError(f"Error al subir el archivo: {e}") from e
