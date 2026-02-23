"""Dependencias de FastAPI, incluyendo autenticación."""

import jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.core.config import settings
from app.core.database import get_session
from app.models.user_model import User
from app.core.security import SECRET_KEY, ALGORITHM, InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.GLOBAL_PREFIX}/auth/login")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    """Extrae el usuario actual a partir del token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Token inválido o expirado")
    
    # Buscar el usuario en la BD
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
        
    return user
