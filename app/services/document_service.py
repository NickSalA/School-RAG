"""Servicio para la gestión de documentos, incluyendo la carga, eliminación y recuperación de documentos subidos por los usuarios."""

import shutil
import tempfile
import os
import aiofiles

from sqlmodel.ext.asyncio.session import AsyncSession

from loguru import logger

from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from httpx import TimeoutException, ConnectError

from app.core.config import settings

from app.models import ResourceType

from app.schemas import LogCreate

from app.repositories import DocumentRepository, LogRepository

from app.adapters.qdrant import AsyncQdrantClient
from app.adapters.llamaparse import get_analyzer

from app.util import clean_content

from app.exceptions.cloud import DocumentAIError, DocumentTimeoutError

class DocumentService:
    def __init__(self, session: AsyncSession | None, client: AsyncQdrantClient):
        self.session = session
        self.log_repo = LogRepository(session) if session else None
        self.index = settings.INDEX_NAME
        self.document_repo = DocumentRepository(client)

    async def read_documents(self, file_path, debug: bool = False):
        """Lee y procesa un documento utilizando el analizador de LlamaParse."""
        parser = get_analyzer()
        document = await parser.aload_data(file_path)

        if debug:
            logger.debug(f"Documento: {file_path} leído y procesado con {len(document)} chunks.")
            for i, chunk in enumerate(document):
                logger.debug(f"Chunk {i} | {len(chunk.get_content())} caracteres | Contenido: {chunk.get_content()[:150]}...")
                return document
        return document

    async def upload_document(self, file, user_id: int, debug: bool = False) -> bool:
        """Carga un documento, lo procesa y lo almacena en el vector store."""
        temp_dir = tempfile.mkdtemp()
        safe_filename = os.path.basename(file.filename)
        temp_path = os.path.join(temp_dir, safe_filename)
        try:
            async with aiofiles.open(temp_path, "wb") as temp_file:
                content = await file.read()
                await temp_file.write(content)

            document = await self.read_documents(temp_path, debug=debug)

            for i, doc in enumerate(document):
                doc.id_ = f"{safe_filename}_doc_{i}"
                doc.metadata["filename"] = safe_filename

            chunks = clean_content(document)

            logger.debug(f"[SERVICE] Enviando {len(chunks)} chunks al repositorio")
            await self.document_repo.upload_document(
                index=self.index,
                filename=safe_filename,
                chunks=chunks
            )
            logger.debug("[SERVICE] Upload al repositorio completado")

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
                logger.debug("[SERVICE] Guardando log en BD...")
                await self.log_repo.create(log)
                logger.debug("[SERVICE] Log guardado exitosamente")
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
