"""Tests de autorización y ownership sobre servicios críticos."""

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

from app.exceptions.auth import PermissionDeniedError
from app.exceptions.database import NotFoundException
from app.models import Role
from app.schemas.user_schema import UserCreate, UserUpdate
from app.services.conversation_service import ConversationService
from app.services.user_service import UserService


def _build_user(user_id: int, role: Role):
    return SimpleNamespace(
        id=user_id,
        name=f"user-{user_id}",
        email=f"user-{user_id}@example.com",
        password="hashed-password",
        role=role,
    )


def test_admin_cannot_create_admin_user() -> None:
    """Solo SUPERADMIN puede crear cuentas con privilegios administrativos."""
    service = UserService(session=None)
    service.user_repo.create = AsyncMock()

    current_user = _build_user(user_id=10, role=Role.ADMIN)
    new_user = UserCreate(
        name="new-admin",
        email="new-admin@example.com",
        password="secret",
        role=Role.ADMIN,
    )

    with pytest.raises(PermissionDeniedError):
        asyncio.run(service.create(new_user, current_user))

    service.user_repo.create.assert_not_awaited()


def test_non_superadmin_cannot_change_roles() -> None:
    """El cambio de roles debe quedar reservado a SUPERADMIN."""
    service = UserService(session=None)
    service.user_repo.get = AsyncMock(
        return_value=_build_user(user_id=11, role=Role.USER)
    )
    service.user_repo.update = AsyncMock()

    current_user = _build_user(user_id=11, role=Role.USER)

    with pytest.raises(PermissionDeniedError):
        asyncio.run(service.update(11, UserUpdate(role=Role.ADMIN), current_user))

    service.user_repo.update.assert_not_awaited()


def test_conversation_service_blocks_access_to_other_users_data() -> None:
    """Las conversaciones ajenas deben responder como inexistentes."""
    service = ConversationService(session=None)
    service.conversation.get = AsyncMock(
        return_value=SimpleNamespace(id=77, user_id=99, content=[], prompt_id=1)
    )

    with pytest.raises(NotFoundException):
        asyncio.run(service.get_for_user(77, user_id=1))
