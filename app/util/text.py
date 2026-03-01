"""Utilidades para procesamiento de texto."""

import re
from typing import List
from llama_index.core import Document

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
    """Limpia el contenido de los documentos eliminando saltos de línea y espacios innecesarios.
    
    También inyecta el nombre del documento al inicio del texto de cada chunk
    para que el modelo de embeddings capture el contexto del documento origen.
    """
    cleaned_docs = []
    for doc in documents:
        content = doc.text
        content = content.replace("\r", " ")
        content = re.sub(r'-\n', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Inyectar el filename al inicio del texto para enriquecer el embedding
        filename = doc.metadata.get("filename", "")
        if filename:
            content = f"Documento: {filename}\n\n{content.strip()}"
        else:
            content = content.strip()

        cleaned_docs.append(Document(text=content, metadata=doc.metadata))
    return cleaned_docs
