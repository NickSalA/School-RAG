"""Tests de autenticación sobre el contrato real del servicio."""

import asyncio
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def _configure_test_env() -> None:
    env_values = {
        "SECRET_KEY": "test-secret-key-with-at-least-32-bytes",
        "ALGORITHM": "HS256",
        "MODEL_API_KEY": "test-model-key",
        "MODEL_SECOND_API_KEY": "test-model-2-key",
        "QDRANT_API_KEY": "test-qdrant-key",
        "LLAMA_PARSE_API_KEY": "test-llamaparse-key",
        "OPENAI_API": "test-openai-key",
        "BETTER_STACK_TOKEN": "",
        "DATABASE_PASSWORD": "test-password",
        "DATABASE_USER": "test-user",
    }
    for key, value in env_values.items():
        os.environ.setdefault(key, value)


_configure_test_env()

from app.core.security import get_password_hash, verify_password
from app.exceptions.auth import InvalidCredentialsError
from app.models import Role
from app.schemas.auth_schema import LoginRequest
from app.services.auth_service import AuthService


def _build_user(password: str, **overrides):
    data = {
        "id": 1,
        "name": "tester",
        "email": "tester@example.com",
        "password": password,
        "role": Role.USER,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def test_verify_password_handles_invalid_hash() -> None:
    """Los hashes corruptos no deben romper el login con un 500."""
    assert verify_password("secret", "invalid-hash") is False


def test_login_rejects_missing_user_without_enumeration() -> None:
    """Usuario inexistente debe responder igual que unas credenciales inválidas."""
    service = AuthService(session=None)
    service.user_repo.get_by_name = AsyncMock(return_value=None)

    with pytest.raises(InvalidCredentialsError, match="Credenciales inválidas"):
        asyncio.run(service.login(LoginRequest(username="ghost", password="secret")))


def test_login_rejects_invalid_hash_as_invalid_credentials() -> None:
    """Un hash corrupto no debe filtrar un stacktrace ni romper la autenticación."""
    service = AuthService(session=None)
    service.user_repo.get_by_name = AsyncMock(
        return_value=_build_user(password="not-a-valid-bcrypt-hash")
    )

    with pytest.raises(InvalidCredentialsError, match="Credenciales inválidas"):
        asyncio.run(service.login(LoginRequest(username="tester", password="secret")))


def test_login_success_returns_token_and_user() -> None:
    """El login válido debe generar un token y devolver el usuario autenticado."""
    service = AuthService(session=None)
    service.user_repo.get_by_name = AsyncMock(
        return_value=_build_user(password=get_password_hash("secret"))
    )

    response = asyncio.run(
        service.login(LoginRequest(username="tester", password="secret"))
    )

    assert response.token_type == "bearer"
    assert response.access_token
    assert response.user.id == 1
    assert response.user.email == "tester@example.com"
