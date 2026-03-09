"""Router para autenticación y gestión de sesiones."""

from typing import Annotated

# FastAPI
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

# Async Session
from sqlmodel.ext.asyncio.session import AsyncSession

# Schemas
from app.schemas.auth_schema import LoginRequest, LoginResponse

# Database
from app.core.database import get_session

# Services
from app.services.auth_service import AuthService

router = APIRouter()

FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/login", response_model=LoginResponse)
async def login(form_data: FormDep, session: SessionDep):
    """
    Endpoint para iniciar sesión.
    """
    credentials = LoginRequest(username=form_data.username, password=form_data.password)

    service = AuthService(session)
    return await service.login(credentials)
