"""Configuración global del proyecto."""

# Pydantic Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError

# Logging
from loguru import logger

# Credenciales Azure
from azure.identity import DefaultAzureCredential

# Manejo de secretos en Key Vault
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError

from app.exceptions.cloud import SecretNotFoundError, SecretEmptyError, AzureAuthError

VAULT_NAME = "kv-school"
KV_URL = f"https://{VAULT_NAME}.vault.azure.net"


class SecretManager:
    """Gestor de secretos con lazy initialization.
    
    El cliente de Azure Key Vault solo se crea cuando se solicita
    el primer secreto, permitiendo que la app inicie sin Azure.
    """
    _client: SecretClient | None = None

    @classmethod
    def _get_client(cls) -> SecretClient:
        """Obtener o crear el cliente de Azure Key Vault."""
        if cls._client is None:
            try:
                logger.debug("Conectando a Azure Key Vault...")
                credential = DefaultAzureCredential()
                cls._client = SecretClient(vault_url=KV_URL, credential=credential)
                logger.debug("Conexión a Azure Key Vault establecida.")
            except Exception as e:
                raise AzureAuthError("Error al obtener credenciales de Azure Key Vault.") from e
        return cls._client

    @classmethod
    def get_secret(cls, name: str) -> str:
        """Wrapper para obtener un secreto de Azure Key Vault.
        
        Args:
            name: Nombre del secreto a recuperar.
        
        Returns:
            Valor del secreto.
        
        Raises:
            SecretNotFoundError: Si el secreto no existe.
            SecretEmptyError: Si el secreto no tiene valor.
            AzureAuthError: Si hay error de autenticación.
        """
        logger.debug(f"Obteniendo secreto: {name}")
        try:
            client = cls._get_client()
            secret = client.get_secret(name)
            if secret.value is None:
                raise SecretEmptyError(f"Secreto {name} no tiene un valor.")
            return secret.value
        except ResourceNotFoundError as e:
            raise SecretNotFoundError(f"Secreto {name} no encontrado en Key Vault.") from e
        except ClientAuthenticationError as e:
            raise AzureAuthError("Error de autenticación al acceder a Key Vault.") from e


def get_secret(name: str) -> str:
    """ Función de conveniencia para obtener secretos, usada en Settings.
    Nota: Esta función solo se llama si no hay valor en .env, gracias a Pydantic.
    """
    return SecretManager.get_secret(name)

class Settings(BaseSettings):
    PROJECT_NAME: str = "SCHOOL-RAG"
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

    INDEX_NAME: str = Field(default="school_rag_index")

    ALLOWED_FILE_TYPES: list[str] = Field(default=["application/pdf", "text/plain"])
    MAX_FILE_SIZE: int = Field(default=5)
    MAX_NUM_PAGES: int = Field(default=10)

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
