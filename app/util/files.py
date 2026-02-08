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
