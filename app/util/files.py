"""Utilidades para sincronización de documentos"""

import os
from typing import List
from qdrant_client.http import models
from qdrant_client import QdrantClient

def get_files(path: str = "") -> List[str]:
    """Lista archivos válidos en una carpeta."""
    if not path or not os.path.isdir(path):
        return []
    files = []
    for element in os.listdir(path):
        full_path = os.path.join(path, element)
        if os.path.isfile(full_path):
            files.append(full_path)
    return files

def delete_collection_points(client: QdrantClient, index: str, key: str, value: str):
    """Elimina puntos de una colección en Qdrant basados en una clave de metadatos."""

    if not client.collection_exists(index):
        return

    client.delete(
        collection_name=index,
        points_selector=models.FilterSelector(
            filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                ]
            )
        )
    )

def ensure_collection_exists(client: QdrantClient, index: str):
    """Asegura que una colección exista en Qdrant, si no existe la crea."""
    if not client.collection_exists(index):
        client.recreate_collection(
            collection_name=index,
            vectors_config=models.VectorParams(
                size=768,
                distance=models.Distance.COSINE
            )
        )
    # Crear índice para filtrar por filename (idempotente)
    try:
        client.create_payload_index(
            collection_name=index,
            field_name="filename",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
    except Exception as e:
        if "already exists" not in str(e):
            raise

def get_collection_points(client: QdrantClient, index: str) -> List[str]:
    """Obtiene puntos de una colección en Qdrant basados en una clave de metadatos."""

    filenames = set()
    next_offset = None

    while True:
        search_result, next_offset = client.scroll(
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
