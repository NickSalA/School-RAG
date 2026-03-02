"""Repositorio para la gestión de documentos, incluyendo la creación, actualización y eliminación de documentos."""

# Librerías para manejo de concurrencia y asincronía
from fastapi.concurrency import run_in_threadpool

# Librerías para manejo de bases de datos y clientes externos
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

# Librerías para manejo de archivos y procesamiento de texto
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core import VectorStoreIndex, StorageContext

# Adapters para servicios externos
from app.adapters.qdrant import get_vector_store, connect_vectorial_client

# Excepciones personalizadas
from app.exceptions.cloud import DocumentAIError

class DocumentRepository:
    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    def get_node_parser(self):
        """Configura y devuelve un parser de nodos."""
        return SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )

    async def ensure_collection(self, index: str):
        """Asegura que la colección de documentos exista en Qdrant."""
        exists = await self.client.collection_exists(collection_name=index)
        if not exists:
            await self.client.recreate_collection(
                collection_name=index,
                vectors_config=models.VectorParams(
                size=768,
                distance=models.Distance.COSINE
                )
            )
        try:
            await self.client.create_payload_index(
                collection_name=index,
                field_name="filename",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
        except (ValueError, RuntimeError) as e:
            if "already exists" not in str(e):
                raise

    async def delete_points_by_filename(self, index: str, filename: str):
        """Elimina puntos de una colección en Qdrant basados en el nombre del archivo (metadato 'filename')."""
        exists = await self.client.collection_exists(collection_name=index)
        if not exists:
            raise DocumentAIError(f"La colección '{index}' no existe en Qdrant.")

        await self.client.delete(
            collection_name=index,
            points_selector=models.FilterSelector(
                filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="filename",
                            match=models.MatchValue(value=filename)
                        )
                    ]
                )
            )
        )

    async def get_all_filenames(self, index: str) -> list[str]:
        """Obtiene una lista de los nombres de los documentos subidos a la colección."""
        exists = await self.client.collection_exists(collection_name=index)
        if not exists:
            raise DocumentAIError(f"La colección '{index}' no existe en Qdrant.")

        filenames = set()
        next_offset = None
        while True:
            search_result, next_offset = await self.client.scroll(
                collection_name=index,
                with_vectors=False,
                with_payload=["filename"],
                offset=next_offset,
                limit=1000
            )
            filenames.update({point.payload.get("filename") for point in search_result if point.payload})
            if next_offset is None:
                break

        filenames.discard(None)
        return list(filenames)

    async def upload_document(self, index: str, filename: str, chunks: list):
        """Sube un documento a Qdrant, creando o actualizando puntos en la colección correspondiente."""
        await self.ensure_collection(index)
        await self.delete_points_by_filename(index, filename)

        sync_client = connect_vectorial_client()
        vector_store = get_vector_store(sync_client, index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        try:
            await run_in_threadpool(
                lambda: VectorStoreIndex.from_documents(
                    chunks,
                    storage_context=storage_context,
                    node_parser=self.get_node_parser(),
                    show_progress=True,
                )
            )
        except Exception as e:
            raise DocumentAIError(f"Error al crear el índice: {e}") from e
        finally:
            sync_client.close()
