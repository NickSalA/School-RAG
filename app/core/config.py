"""Configuración global del proyecto."""

# Pydantic Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError

# Exceptions
from app.exceptions.cloud import SecretNotFoundError

class Settings(BaseSettings):
    PROJECT_NAME: str = "PUCP API"
    LOG_LEVEL: str = "INFO"
    GLOBAL_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://localhost:3000"]
    SECRET_KEY: str = Field(default=...)

    MODEL_API_KEY: str = Field(default=...)
    MODEL_TEMPERATURE: float = 0.7

    GEMINI_EMBEDDING_MODEL_NAME: str = Field(default=...)
    
    QDRANT_HOST: str = Field(default=...)
    QDRANT_PORT: int = Field(default=6333)

    LLAMA_PARSE_API_KEY: str = Field(default=...)
    
    BETTER_STACK_TOKEN: str = Field(default=...)
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
