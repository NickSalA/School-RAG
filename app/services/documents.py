"""Subida y sincronización de documentos con Azure Cognitive Search."""

# Utilitarios para sincronización de documentos con Azure Cognitive Search
import os
import time
import shutil
import tempfile

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser

# Excepciones de servicios externos
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from httpx import TimeoutException, ConnectError

# Adapters para servicios externos
from app.adapters.qdrant import get_vector_store, connect_vectorial_client
from app.adapters.llamaparse import get_analyzer
from app.adapters.gemini import configure_embedding

# Utilitarios para procesamiento de texto y manejo de archivos
from app.util.text import clean_content
from app.util.files import get_files, delete_collection_points, ensure_collection_exists, get_collection_points

# Excepciones personalizadas
from app.exceptions.cloud import DocumentAIError, DocumentTimeoutError

def read_document(file_path: str):
    """Lee y procesa un documento usando LlamaParse."""

    parser = get_analyzer()
    document = parser.load_data(file_path)
    return document

def get_node_parser():
    """Configura y devuelve un parser de nodos de ventana de oraciones."""
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    return node_parser

def upload_file_path(file_path:str, index: str) -> bool:
    """Sube un archivo al vector store después de procesarlo y crear un índice."""
    client = connect_vectorial_client()
    ensure_collection_exists(client, index)
    vector_store = get_vector_store(client, index)

    try:
        node_parser = get_node_parser()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        filename = os.path.basename(file_path)

        delete_collection_points(client, index, "filename", filename)
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
    except (TimeoutException, ConnectError) as e:
        raise DocumentTimeoutError(f"Timeout al conectar con Qdrant: {e}") from e
    except (ResponseHandlingException, UnexpectedResponse) as e:
        raise DocumentAIError(f"Error en respuesta de Qdrant: {e}") from e
    except Exception as e:
        raise DocumentAIError(f"Error al crear el índice: {e}") from e

def upload_file(file, index: str) -> bool:
    """Sube un archivo recibido a través de la API al vector store después de procesarlo."""
    temp_dir = tempfile.mkdtemp()
    try:
        safe_filename = os.path.basename(file.filename)
        temp_path = os.path.join(temp_dir, safe_filename)
        with open(temp_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        return upload_file_path(temp_path, index)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def upload_files_from_folder(folder_path: str = "", index: str = ""):
    """Carga todos los archivos de una carpeta a la base de conocimiento."""
    error_folder = os.path.join(folder_path, "error_files")
    configure_embedding()
    while True:
        print("Ejecutando sincronización...")
        archivos = get_files(folder_path)

        if archivos:
            for file_path in archivos:
                filename = os.path.basename(file_path)

                # Evitar procesar archivos temporales o de sistema
                if filename.startswith(".") or filename == "error_files":
                    continue

                print(f"procesando: {filename}...")

                success = upload_file_path(file_path, index)

                if success:
                    try:
                        os.remove(file_path)
                        print(f"{filename} procesado y eliminado.")
                    except OSError as e:
                        print(f"⚠️ Error al borrar archivo {filename}: {e}")
                else:
                    print(f"{filename} tiene errores. Moviendo a carpeta de revisión.")
                    os.makedirs(error_folder, exist_ok=True)

                    timestamp = int(time.time())
                    destino = os.path.join(error_folder, f"{timestamp}_{filename}")
                    shutil.move(file_path, destino)
        time.sleep(5)

def get_uploaded_documents(index: str) -> list[str]:
    """Obtiene una lista de los documentos subidos a la colección."""
    client = connect_vectorial_client()
    try:
        if not client.collection_exists(index):
            raise DocumentAIError(f"La colección '{index}' no existe en el vector store.")
        return get_collection_points(client, index)
    except (TimeoutException, ConnectError) as e:
        raise DocumentTimeoutError(f"Timeout al conectar con Qdrant: {e}") from e
    except (ResponseHandlingException, UnexpectedResponse) as e:
        raise DocumentAIError(f"Error en respuesta de Qdrant: {e}") from e
    except DocumentAIError:
        raise
    except Exception as e:
        raise DocumentAIError(f"Error al obtener los documentos subidos: {e}") from e
