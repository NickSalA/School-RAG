"""Router para autenticación y gestión de sesiones."""

from fastapi import APIRouter, Depends

from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.auth_schema import LoginRequest, LoginResponse
from app.core.database import get_session
from app.services.auth import AuthService

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, session: AsyncSession = Depends(get_session)):
    """
    Endpoint para iniciar sesión.
    """
    service = AuthService(session)
    return await service.login(credentials)