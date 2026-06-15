"""Dependencias de FastAPI, incluyendo autenticación."""

from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.exceptions.auth import InvalidCredentialsError, PermissionDeniedError
from app.models import Role
from app.models.user_model import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.GLOBAL_PREFIX.lstrip('/')}/auth/login"
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Extrae el usuario actual a partir del token JWT."""

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError("Token inválido o expirado.")
        user_id_int = int(user_id)
    except (jwt.PyJWTError, ValueError) as e:
        raise InvalidCredentialsError("Token inválido o expirado.") from e

    query = select(User).where(User.id == user_id_int)
    result = await session.exec(query)
    user = result.first()
    if not user:
        raise InvalidCredentialsError("Token inválido o expirado.")
    return user


def require_roles(*allowed_roles: Role):
    """Construye una dependencia que exige uno de los roles permitidos."""

    async def role_dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise PermissionDeniedError(
                "No tienes permisos para acceder a este recurso."
            )
        return current_user

    return role_dependency
