"""Utilidades para sincronización de documentos y procesamiento de texto."""

import os
import re
from typing import List
from llama_index.core import Document
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

def clean_text(text: str) -> str:
    """
    Limpieza robusta para eliminar ruido de conversión (tablas rotas, headers repetidos).
    """
    if not text:
        return ""
    text = text.replace("\r", " ")
    text = text.replace('""', '"')

    # Colapsar espacios múltiples y saltos de línea excesivos
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def clean_content(documents: List[Document]):
    """Limpia el contenido de los documentos eliminando saltos de línea y espacios innecesarios."""
    cleaned_docs = []
    for doc in documents:
        content = doc.text
        content = content.replace("\r", " ")
        content = re.sub(r'-\n', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        cleaned_docs.append(Document(text=content.strip(), metadata=doc.metadata))
    return cleaned_docs

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
