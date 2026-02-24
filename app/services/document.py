"""Servicio para la gestión de documentos, incluyendo la carga, eliminación y recuperación de documentos subidos por los usuarios."""

import shutil
import tempfile
import os
import aiofiles

from sqlmodel.ext.asyncio.session import AsyncSession

from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from httpx import TimeoutException, ConnectError

from app.core.config import settings

from app.models.log_model import ResourceType

from app.schemas.log_schema import LogCreate

from app.repositories.document_repository import DocumentRepository
from app.repositories.log_repository import LogRepository

from app.adapters.qdrant import AsyncQdrantClient
from app.adapters.llamaparse import get_analyzer

from app.util.text import clean_content

from app.exceptions.cloud import DocumentAIError, DocumentTimeoutError

class DocumentService:
    def __init__(self, session: AsyncSession | None, client: AsyncQdrantClient):
        self.session = session
        self.log_repo = LogRepository(session) if session else None
        self.index = settings.INDEX_NAME
        self.document_repo = DocumentRepository(client)

    async def read_documents(self, file_path):
        """Lee y procesa un documento utilizando el analizador de LlamaParse."""
        parser = get_analyzer()
        document = parser.aload_data(file_path)
        return await document

    async def upload_document(self, file, user_id: int) -> bool:
        """Carga un documento, lo procesa y lo almacena en el vector store."""
        temp_dir = tempfile.mkdtemp()
        safe_filename = os.path.basename(file.filename)
        temp_path = os.path.join(temp_dir, safe_filename)
        try:
            async with aiofiles.open(temp_path, "wb") as temp_file:
                content = await file.read()
                await temp_file.write(content)

            document = await self.read_documents(temp_path)

            for i, doc in enumerate(document):
                doc.id_ = f"{safe_filename}_doc_{i}"
                doc.metadata["filename"] = safe_filename

            chunks = clean_content(document)

            await self.document_repo.upload_document(
                index=self.index,
                filename=safe_filename,
                chunks=chunks
            )

            log = LogCreate(
                resource_type=ResourceType.QDRANT_COLLECTION,
                resource_id=safe_filename,
                action="upload",
                user_id=user_id,
                details={
                    "content_type": file.content_type,
                    "num_chunks": len(chunks),
                    "size_bytes": file.size,
                    "index": self.index
                }
            )

            if self.log_repo:
                await self.log_repo.create(log)
            return True
        except (TimeoutException, ConnectError) as e:
            raise DocumentTimeoutError(f"Timeout al conectar con Qdrant: {e}") from e
        except (ResponseHandlingException, UnexpectedResponse) as e:
            raise DocumentAIError(f"Error en respuesta de Qdrant: {e}") from e
        except Exception as e:
            raise DocumentAIError(f"Error al crear el índice: {e}") from e
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    async def delete_document(self, filename: str, user_id: int) -> bool:
        """Elimina un documento del vector store."""
        await self.document_repo.delete_points_by_filename(
            index=self.index,
            filename=filename
        )

        log = LogCreate(
            resource_type=ResourceType.QDRANT_COLLECTION,
            resource_id=filename,
            action="delete",
            user_id=user_id,
            details={
                "index": self.index,
            }
        )
        if self.log_repo:
            await self.log_repo.create(log)
        return True

    async def get_uploaded_documents(self) -> list[str]:
        """Obtiene una lista de los nombres de los documentos subidos."""
        return await self.document_repo.get_all_filenames(index=self.index)
