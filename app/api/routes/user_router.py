"""Router para el flujo de usuarios."""

from typing import Annotated
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.user_schema import UserRead, UserCreate, UserUpdate
from app.api.dependencies.dep_chat import get_flow_agent
from app.core.database import get_session

from app.services.user import UserService

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """Endpoint para crear un nuevo usuario."""
    service = UserService(session)
    return await service.create(user_in)
