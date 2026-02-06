"""Configuración global del proyecto."""

# Pydantic Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError

# Exceptions
from loguru import logger

# Credenciales Azure
from azure.identity import DefaultAzureCredential

# Manejo de secretos en Key Vault
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

from app.exceptions.cloud import SecretNotFoundError, SecretEmptyError, AzureAuthError

VAULT_NAME = "kv-school"
KV_URL = f"https://{VAULT_NAME}.vault.azure.net"

try:
    logger.debug("Obteniendo credenciales de Azure Key Vault...")
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=KV_URL, credential=credential)
    logger.debug("Credenciales obtenidas correctamente.")

except Exception as e:
    raise AzureAuthError("Error al obtener credenciales de Azure Key Vault.") from e

def get_secret(name: str) -> str:
    """
    Recupera el valor de un secreto desde Azure Key Vault.
    Args:
        name (str): Nombre del secreto a recuperar.
    Returns:
        str: Valor del secreto.
    """
    logger.debug(f"Obteniendo secreto: {name}")
    try:
        secret = client.get_secret(name)
        if secret.value is None:
            raise SecretEmptyError(f"Secreto {name} no tiene un valor.")
        return secret.value
    except ResourceNotFoundError as e:
        raise SecretNotFoundError(f"Secreto {name} no encontrado en Key Vault.") from e
    except ClientAuthenticationError as e:
        raise AzureAuthError("Error de autenticación al acceder a Key Vault.") from e

class Settings(BaseSettings):
    PROJECT_NAME: str = "PUCP API"
    LOG_LEVEL: str = "INFO"
    GLOBAL_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://localhost:3000"]
    SECRET_KEY: str = Field(default_factory=lambda: get_secret("SECRET-KEY"))

    MODEL_API_KEY: str = Field(default_factory=lambda: get_secret("MODEL-API-KEY"))
    MODEL_TEMPERATURE: float = 0.7

    GEMINI_EMBEDDING_MODEL_NAME: str = Field(default=...)

    QDRANT_HOST: str = Field(default=...)
    QDRANT_PORT: int = Field(default=6333)

    LLAMA_PARSE_API_KEY: str = Field(default_factory=lambda: get_secret("LLAMA-PARSE-API-KEY"))

    BETTER_STACK_TOKEN: str = Field(default_factory=lambda: get_secret("BETTER-STACK-TOKEN"))
    BETTER_STACK_HOST: str = Field(default=...)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

try:
    settings = Settings()
except ValidationError as e:
    raise SecretNotFoundError(f"Error de configuración: {e}") from e
