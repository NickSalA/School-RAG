"""Dependencias de FastAPI, incluyendo autenticación."""

from typing import Annotated
import jwt

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.models.user_model import User

from app.exceptions.auth import InvalidCredentialsError, UserNotFoundError, TokenValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.GLOBAL_PREFIX}/auth/login")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)]
) -> User:
    """Extrae el usuario actual a partir del token JWT."""

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise InvalidCredentialsError("Usuario no identificado en el token")

    except jwt.InvalidTokenError as e:
        raise InvalidCredentialsError(f"Token inválido o expirado: {e}") from e

    except jwt.PyJWTError as e:
        raise TokenValidationError(f"Error al validar el token: {e}") from e

    query = select(User).where(User.id == int(user_id))
    result = await session.exec(query)
    user = result.first()
    if not user:
        raise UserNotFoundError("Usuario no encontrado en la base de datos")
    return user
