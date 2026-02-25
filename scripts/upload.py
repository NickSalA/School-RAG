"""Script para subir archivos desde una carpeta específica al sistema de almacenamiento."""
import os
from scripts.documents import upload_files_from_folder
from app.core.config import settings
# Obtiene la ruta absoluta de la carpeta 'files' dentro de 'app'
APP_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_FOLDER = os.path.join(APP_DIR, "files")

if not os.path.exists(FILES_FOLDER):
    print("⚠️ La carpeta de archivos no existe. Por favor, crea la carpeta 'files' dentro de 'app'.")

upload_files_from_folder(FILES_FOLDER, index=settings.INDEX_NAME)
