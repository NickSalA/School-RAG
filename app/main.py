"""Aplicación principal de FastAPI para el backend de School-RAG."""
# Sistema
import sys

# Logging
from loguru import logger

# FastAPI
from fastapi import FastAPI
from pydantic import ValidationError

# Uvicorn para correr la app
import uvicorn

# Excepciones personalizadas
from app.exceptions.cloud import AzureAuthError

# Importar gestor de secretos
try:
    from app.factory import create
    app: FastAPI = create()
    logger.debug("Configuración importada correctamente.")
except AzureAuthError as e:
    logger.exception(f"Error de autenticación con Azure Key Vault: {e}")
    sys.exit(1)
except ValidationError as e:
    logger.exception(f"Error de validación en la configuración (Pydantic): {e}")
    sys.exit(1)
except ValueError as e:
    logger.exception(f"Error de valor en la configuración: {e}")
    sys.exit(1)
except Exception as e: # pylint: disable=broad-except
    logger.exception(f"  al importar la configuración: {e}")
    sys.exit(1)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_config=None)
