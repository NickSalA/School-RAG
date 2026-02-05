"""Subida y sincronización de documentos con Azure Cognitive Search."""

# Utilitarios para sincronización de documentos con Azure Cognitive Search
import os, time, shutil
from llama_index.core import Settings
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceWindowNodeParser

# Helpers propios
from app.core.knowledge import get_vector_store, get_analyzer, connect_vectorial_client
from app.util.sincronizer import clean_content, get_files, delete_collection_points

# Configuración y excepciones
from app.core.config import settings
from app.exceptions.cloud import DocumentAIError

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
    except Exception as e:
        raise DocumentAIError(f"Error al crear el índice: {e}") from e

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

                success = upload_file(file_path, index)

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
