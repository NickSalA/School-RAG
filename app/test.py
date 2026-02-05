from fsspec.spec import conf
from httpx import get
from llama_index.core import Document, VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from qdrant_client.http import models

from app.core.knowledge import get_analyzer, connect_vectorial_client, get_vector_store
import re
import os
from qdrant_client import QdrantClient
from typing import List
from llama_parse import LlamaParse, ResultType
from llama_index.core import Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

from app.core.config import settings
from app.exceptions.cloud import DocumentAIError

def read_document(file_path: str):
    """Lee y procesa un documento usando LlamaParse."""

    parser = get_analyzer()
    document = parser.load_data(file_path)
    return document

def clean_content(documents: List[Document]) -> List[Document]:
    """Limpia el contenido de los documentos eliminando saltos de línea y espacios innecesarios."""
    cleaned_docs: List[Document] = []
    for doc in documents:
        content = doc.text
        content = content.replace("\r", " ")
        content = re.sub(r'-\n', '', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        cleaned_docs.append(Document(text=content.strip(), metadata=doc.metadata))
    return cleaned_docs

def get_node_parser():
    """Configura y devuelve un parser de nodos de ventana de oraciones."""
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    return node_parser

def configure_embedding():
    """Configura el modelo de embedding Google GenAI para su uso en el proyecto."""
    Settings.embed_model = GoogleGenAIEmbedding(
        model_name=settings.GEMINI_EMBEDDING_MODEL_NAME,
        api_key=settings.MODEL_API_KEY,
    )

def upload_file(file_path:str, index: str) -> bool:
    """Sube un archivo al vector store después de procesarlo y crear un índice."""
    client = connect_vectorial_client()
    vector_store = get_vector_store(client, index)
    node_parser = get_node_parser()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    filename = os.path.basename(file_path)
    try:
        client.delete(
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
        document = read_document(file_path)

        for i, doc in enumerate(document):
            doc.id_ = f"{filename}_doc_{i}"
            doc.metadata["filename"] = filename
        chunks = clean_content(document)

        VectorStoreIndex.from_documents(
            chunks,
            storage_context=storage_context,
            node_parser=node_parser,
            show_progress=True,
        )
        return True

    except Exception as e:
        raise DocumentAIError(f"Error al crear el índice: {e}") from e

#configure_embedding()
#hi = upload_file("/home/daminin/Documents/Repositorios/School-RAG/app/files/OpcionB2_Creditos_PRONABEC_RAG_v2.pdf", "test_collection")